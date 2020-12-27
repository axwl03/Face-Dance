from PyQt5.QtWidgets import QWidget, QLabel, QLCDNumber, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtCore import QRect, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QImage, QPixmap

import threading
import cv2
import time

from netModule import NetModule
from emoji import Emoji
from imageModule import ImgModule

class GamePage(QWidget):
    changePixmapItem = pyqtSignal(QImage)

    def __init__(self, isServer, ip):
        self.__WIDTH = 1078
        self.__HEIGHT = 767
        self.__font = QFont()
        self.__font.setFamily("Arial Black")
        self.__font.setPointSize(18)
        self.__font.setBold(True)
        self.__font.setWeight(75)
        super(GamePage, self).__init__()
        self.resize(self.__WIDTH, self.__HEIGHT)
        self.setWindowTitle("Game Page")
        
        self.changePixmapItem.connect(self.setFaceImage)
        self.__isServer = isServer
        self.__ip = ip

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

        self.__faceImageThread = threading.Thread(target=self.convertFaceImage)

        # self.__net = NetModule(self)
        # self.__runner = threading.Thread(target=self.startGame)
        # self.__runner.start()
    
        # self.__camera.frame = None # for setFaceImage
        # self.__camera.state = 'None' # for setResult


        e = Emoji(200, 200, Emoji.ANGRY)
        self.setEmoji(e)

        self.__camera = ImgModule()
        # self.__camera.setFPS(1)
        self.__camera.start()
        self.__faceImageThread.start()

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


    def printResult(self):
        while True:
            print(self.__camera.state)
            time.sleep(1)
        
    def startGame(self):
        if self.isServer == True:
            self.__net.listen(self.__port)
        else:
            self.__net.connect(self.ip, self.__port)
        self.__runner2 = threading.Thread(target=self.printResult)
        self.__runner2.start()
 
        while True:
            msg = input()
            if msg != 'exit':
                self.__net.sendData(msg)
            else:
                self.__net.close()
                break
    
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

    # set emoji on screen
    def setEmoji(self, e):
        self.__pic = QGraphicsPixmapItem()
        self.__pic.setPixmap(e.getPic().scaled(50, 50))
        self.__pic.setPos(e.getX(), e.getY())
        self.__scene.addItem(self.__pic)
