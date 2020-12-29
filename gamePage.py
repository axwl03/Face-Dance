from PyQt5.QtWidgets import QWidget, QLabel, QLCDNumber, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtCore import QRect, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QImage, QPixmap

import threading
import cv2
import time
import random

from netModule import NetModule
from emoji import Emoji
# from imageModule import ImgModule

class GamePage(QWidget):
    # changePixmapItem = pyqtSignal(QImage)
    maxEmojiNum = 8
    maxEmojiGen = 1
    maxX = 450
    maxY = 500
    myOffsetX = 500
    myOffsetY = 200
    duration = 30
    shift = 2
    width = 1078
    height = 767

    def __init__(self, isServer, ip):
        self.__status = 0   # 0: not started, 1: started, 2: ended
        self.__font = QFont()
        self.__font.setFamily("Arial Black")
        self.__font.setPointSize(18)
        self.__font.setBold(True)
        self.__font.setWeight(75)
        super(GamePage, self).__init__()
        self.resize(self.width, self.height)
        self.setWindowTitle("Game Page")
        
        # self.changePixmapItem.connect(self.setFaceImage)
        self.__isServer = isServer
        self.__ip = ip
        self.__myScore = 0
        self.__enemyScore = 0

        self.__label = QLabel(str(self.__ip), self)
        self.__label.setGeometry(QRect(650, 130, 58, 15))
        self.createLCD()
        self.__graphicsView = QGraphicsView(self)
        self.__graphicsView.setGeometry(QRect(20, 160, 1031, 591))
        self.__scene = QGraphicsScene(self)
        self.__scene.setSceneRect(0, 0, 1000, 589)
        self.__graphicsView.setScene(self.__scene)
        self.__faceImage = QGraphicsPixmapItem()
        self.__faceImage.setPos(50, 50)
        self.__scene.addItem(self.__faceImage)

        self.__matchedEmoji = Emoji.NONE
        self.__emojiList = []
        self.__myEmojiList = []
        self.__port = 8080

        # self.__faceImageThread = threading.Thread(target=self.convertFaceImage)

        self.__net = NetModule(self)
        self.__runner = threading.Thread(target=self.startGame)
        self.__runner.start()
    
        # self.__camera.frame = None # for setFaceImage
        # self.__camera.state = 'None' # for setResult

        # e = Emoji(200, 200, Emoji.ANGRY)
        # self.setEmoji(e)

        # self.__camera = ImgModule()
        # self.__camera.setFPS(1)
        # self.__camera.start()
        # self.__faceImageThread.start()

    def createLCD(self):
        self.__lcd = QLCDNumber(self)
        self.__lcd.setGeometry(QRect(470, 60, 151, 91))
        self.__lcd.setFont(self.__font)
        self.__lcd2 = QLCDNumber(self)
        self.__lcd2.setGeometry(QRect(800, 100, 121, 51))
        self.__lcd2.setFont(self.__font)
        self.__lcd3 = QLCDNumber(self)
        self.__lcd3.setGeometry(QRect(170, 100, 121, 51))
        self.__lcd3.setFont(self.__font)

    def startGame(self):
        if self.__isServer == True:
            self.__net.listen(self.__port)
            self.__action()
        else:
            self.__net.connect(self.ip, self.__port)
            self.__action()

    def __action(self):
        if self.__isServer == True:
            # remove emoji if its status is 2 (out)
            i = 0
            while i < len(self.__myEmojiList):
                if self.__myEmojiList[i].getStatus() == 2:
                    del self.__myEmojiList[i]
                    continue
                i = i + 1

            # randomly generate emoji and append to myEmojiList
            self.__randomGenEmoji()
            for emoji in self.__emojiList:
                newEmoji = Emoji(emoji.getX() + self.myOffsetX, emoji.getY() + self.myOffsetY, emoji.getType())
                self.__myEmojiList.append(newEmoji)

            # send new emojiList
            data = 'new\n'
            for emoji in self.__emojiList:
                data = data + emoji.toString() + '\n'
            self.__net.sendData(data)

            #  send our score
            data = 'score\n' + str(self.__myScore) + '\n'
            self.__net.sendData(data)
        else:
            # remove emoji if its status is 2 (out)
            i = 0
            while i < len(self.__myEmojiList):
                if self.__myEmojiList[i].getStatus() == 2:
                    del self.__myEmojiList[i]
                    continue
                i = i + 1

            # send score to enemy
            data = 'score\n' + str(self.__myScore) + '\n'
            self.__net.sendData(data)
        self.__actioner = threading.Timer(1, self.__action)
        self.__actioner.start()
 
    # set result that predicted by image module
    def setResult(self, emojiType):
        self.__matchedEmoji = emojiType

    # set face image which is obtained from webcam
    def convertFaceImage(self):
        while self.__camera.frame.all() != None:
            rgbImage = cv2.cvtColor(self.__camera.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmapItem.emit(p)
            time.sleep(0.1)

    @pyqtSlot(QImage)
    def setFaceImage(self, image):
        self.__faceImage.setPixmap(QPixmap.fromImage(image))

    def __renderEmoji(self):
        while self.__status != 2:
            if self.__status == 1:
                for emoji in self.__myEmojiList:
                    self.setEmoji(emoji)
            time.sleep(0.5)
    
    # set emoji or add emoji on screen
    def setEmoji(self, e):
        if e.getStatus() == 0:  # new
            e.graphicPixmapItem = QGraphicsPixmapItem()
            e.graphicPixmapItem.setPixmap(e.getPic().scaled(50, 50))
            e.graphicPixmapItem.setPos(e.getX(), e.getY())
            e.setStatus(1)
            self.__scene.addItem(e.graphicPixmapItem)
        elif e.getStatus() == 1:    # exist
            e.setY(e.getY() + self.shift)
            e.graphicPixmapItem.setPos(e.getX(), e.getY())
            if e.getY() > self.myOffsetY + self.maxY:
                e.setStatus(2)
        else:   # out
            self.__scene.removeItem(e.graphicPixmapItem)
            
    def __randomGenEmoji(self):
        if len(self.__emojiList) >= self.maxEmojiNum:
            return
        else:
            tempList = []
            for i in range(self.maxEmojiGen):
                tempList.append(Emoji(random.randint(0, self.maxX), 0, random.randint(1, Emoji.SURPRISE)))
            self.__emojiList = tempList

    def myEmojiAdd(self, emoji):
        self.__myEmojiList.append(emoji)

    def setEnemyScore(self, score):
        self.__enemyScore = score

    def printEmojiList(self):
        print('len: ', len(self.__myEmojiList))
        for emoji in self.__myEmojiList:
            print('{},{} {}'.format(emoji.getX(), emoji.getY(), emoji.getType()))

    def closeEvent(self, event):
        self.__status = 2
        self.__actioner.cancel()
        try:
            self.__net.close()
        except:
            pass
        event.accept()
