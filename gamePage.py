from PyQt5.QtWidgets import QWidget, QLabel, QLCDNumber, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtCore import QRect, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QImage, QPixmap, QPalette, QBrush

import threading
import cv2
import time
import random

from netModule import NetModule
from emoji import Emoji

class GamePage(QWidget):
    changePixmapItem = pyqtSignal(QImage)
    renderSignal = pyqtSignal()
    timeSignal = pyqtSignal()
    gameEnd = pyqtSignal()
    maxEmojiNum = 8
    maxEmojiGen = 1
    maxX = 450
    maxY = 500
    myOffsetX = 500
    myOffsetY = 200
    duration = 30
    shift = 4
    width = 1100
    height = 800

    def __init__(self, isServer, ip, camera):
        self.__status = 0   # 0: not started, 1: started, 2: ended
        self.__font = QFont()
        self.__font.setFamily("Arial Black")
        self.__font.setPointSize(18)
        self.__font.setBold(True)
        self.__font.setWeight(75)
        super(GamePage, self).__init__()
        self.resize(self.width, self.height)
        self.setWindowTitle("Game Page")
        
        self.changePixmapItem.connect(self.setFaceImage)
        self.renderSignal.connect(self.__renderEmojiAction)
        self.timeSignal.connect(self.__displayTimeAction)
        self.gameEnd.connect(self.__finalResult)
        self.__isServer = isServer
        self.__ip = ip
        self.__myScore = 0
        self.__enemyScore = 0

        self.createLCD()
        self.__graphicsView = QGraphicsView(self)
        self.__graphicsView.setGeometry(QRect(33, 160, 1031, 591))
        self.__scene = QGraphicsScene(self)
        self.__scene.setSceneRect(0, 0, 1000, 589)
        self.__graphicsView.setScene(self.__scene)
        self.__faceImage = QGraphicsPixmapItem()
        self.__faceImage.setPos(50, 50)
        self.__scene.addItem(self.__faceImage)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/game_background.jpg")))
        self.setPalette(palette)

        self.__matchedEmoji = Emoji.NONE
        self.__emojiList = []
        self.__myEmojiList = []
        self.__myEmojiListLock = threading.Lock()
        self.__port = 8080
        self.__net = NetModule(self)
        self.__runner = threading.Thread(target=self.startGame)
        self.__runner.start()

        self.__camera = camera
        self.__camera.setFPS(1)
        self.__camera.capture()
        self.__convertFaceImage()

    def createLCD(self):
        self.__timeLCD = QLCDNumber(self)
        self.__timeLCD.setGeometry(QRect(470, 60, 151, 91))
        self.__timeLCD.setFont(self.__font)
        self.__enemyScoreLCD = QLCDNumber(self)
        self.__enemyScoreLCD.setGeometry(QRect(800, 100, 121, 51))
        self.__enemyScoreLCD.setFont(self.__font)
        self.__myScoreLCD = QLCDNumber(self)
        self.__myScoreLCD.setGeometry(QRect(170, 100, 121, 51))
        self.__myScoreLCD.setFont(self.__font)

    def startGame(self):
        try:
            if self.__isServer == True:
                self.__net.listen(self.__port)
            else:
                self.__net.connect(self.__ip, self.__port)
            self.__camera.predict()
            self.__status = 1
            self.__startTime = time.time()
            self.__displayTime()
            self.__action()
            self.__renderEmoji()
        except Exception as e:
            print('error in startGame():', e)

    def __action(self):
        if self.__status == 2:   # game ended
            data = 'final\n' + str(self.__myScore) + '\n'
            self.__net.sendData(data)
            return
        try:
            if self.__isServer == True:
                # remove emoji if its status is 2 (out)
                i = 0
                self.__myEmojiListLock.acquire()
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
                self.__myEmojiListLock.release()

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
                self.__myEmojiListLock.acquire()
                while i < len(self.__myEmojiList):
                    if self.__myEmojiList[i].getStatus() == 2:
                        del self.__myEmojiList[i]
                        continue
                    i = i + 1
                self.__myEmojiListLock.release()

                # send score to enemy
                data = 'score\n' + str(self.__myScore) + '\n'
                self.__net.sendData(data)
            self.__actioner = threading.Timer(0.8, self.__action)
            self.__actioner.start()
        except Exception as e:
            print('error in __action():', e)
 
    # set result that predicted by image module
    def setResult(self, emojiType):
        self.__matchedEmoji = emojiType

    # set face image which is obtained from webcam
    def __convertFaceImage(self):
        if(self.__camera.frame.size != 0):
            rgbImage = cv2.cvtColor(self.__camera.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmapItem.emit(p)
            self.__CFIRunner = threading.Timer(0.04, self.__convertFaceImage)
            self.__CFIRunner.start()

    @pyqtSlot(QImage)
    def setFaceImage(self, image):
        self.__faceImage.setPixmap(QPixmap.fromImage(image))

    def __renderEmoji(self):
        self.renderSignal.emit()
        self.__renderEmojiRunner = threading.Timer(0.02, self.__renderEmoji)
        self.__renderEmojiRunner.start()

    @pyqtSlot()
    def __renderEmojiAction(self):
        if self.__status == 1:
            self.__myEmojiListLock.acquire()
            for emoji in self.__myEmojiList:
                self.setEmoji(emoji)
            self.__myEmojiListLock.release()

    def __displayTime(self):
        self.__elapseTime = time.time() - self.__startTime
        self.timeSignal.emit()
        if int(self.__elapseTime) == self.duration:
            self.__status = 2
            return
        self.__displayTimeRunner = threading.Timer(1, self.__displayTime)
        self.__displayTimeRunner.start()

    @pyqtSlot()
    def __displayTimeAction(self):
        self.__timeLCD.display(int(self.__elapseTime))
    
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
                self.__scene.removeItem(e.graphicPixmapItem)
            elif e.getType() == self.__matchedEmoji:
                self.__myScore = self.__myScore + 10
                self.__myScoreLCD.display(self.__myScore)
                e.setStatus(2)
                self.__scene.removeItem(e.graphicPixmapItem)
        else:   # out
            pass
        self.__enemyScoreLCD.display(self.__enemyScore)
            
    def __randomGenEmoji(self):
        if len(self.__emojiList) >= self.maxEmojiNum:
            return
        else:
            tempList = []
            for i in range(self.maxEmojiGen):
                tempList.append(Emoji(random.randint(0, self.maxX), 0, random.randint(1, Emoji.SURPRISE)))
            self.__emojiList = tempList

    def myEmojiAdd(self, emoji):
        self.__myEmojiListLock.acquire()
        self.__myEmojiList.append(emoji)
        self.__myEmojiListLock.release()

    def setEnemyScore(self, score):
        self.__enemyScore = score

    @pyqtSlot()
    def __finalResult(self):
        # display final result (self.__myScore, self.__enemyScore)
        print('final result get')
        try:
            self.__net.close()
        except:
            pass

    def printEmojiList(self):
        print('len: ', len(self.__myEmojiList))
        for emoji in self.__myEmojiList:
            print('{},{} {}'.format(emoji.getX(), emoji.getY(), emoji.getType()))

    def closeEvent(self, event):
        if hasattr(self, '_GamePage__actioner'):
            self.__actioner.cancel()
        if hasattr(self, '_GamePage__renderEmojiRunner'):
            self.__renderEmojiRunner.cancel()
        if hasattr(self, '_GamePage__displayTimeRunner'):
            self.__displayTimeRunner.cancel()
        self.__status = 2
        if self.__net.isListening():
            self.__net.stopListen()
        
        self.__CFIRunner.cancel()
        self.__camera.stop()
        self.__camera.release()
        self.__camera.captureThread.cancel()
        self.__camera.predictThread.cancel()
        
        try:
            self.__net.close()
        except:
            pass
        event.accept()
