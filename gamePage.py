from PyQt5.QtWidgets import QWidget, QLabel, QLCDNumber, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtCore import QRect, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QImage, QPixmap, QPalette, QBrush, QPen
from PyQt5 import QtMultimedia, QtCore

import threading
import cv2
import time
import random
import os

from netModule import NetModule
from emoji import Emoji

class GamePage(QWidget):
    changePixmapItem = pyqtSignal(QImage)
    renderSignal = pyqtSignal()
    timeSignal = pyqtSignal()
    gameEnd = pyqtSignal()
    maxEmojiNum = 8
    maxEmojiGen = 1
    maxX = 550
    maxY = 450
    myOffsetX = 650
    myOffsetY = 50
    duration = 30
    shift = 4
    width = 1300
    height = 800

    def __init__(self, isServer, ip, camera, musicPlayer):
        self.__status = 0   # 0: not started, 1: started, 2: ended
        super(GamePage, self).__init__()
        self.resize(self.width, self.height)
        self.setWindowTitle("Game Page")
        self.setFixedSize(self.size())
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
        self.__graphicsView.setGeometry(QRect(0, 160, 1300, 600))
        self.__graphicsView.setStyleSheet("background: transparent; border:0px")
        self.__scene = QGraphicsScene(self)
        self.__scene.setSceneRect(0, 0, 1250, 550)
        self.__graphicsView.setScene(self.__scene)
        self.__faceImage = QGraphicsPixmapItem()
        self.__faceImage.setPos(-10, 50)
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

        self.__camera = camera
        self.__camera.setFPS(5)
        self.__camera.capture()
        self.__convertFaceImage()
        self.__musicPlayer = musicPlayer
        # self.__musicPlayer.stop()
        filepath = 'resources/gameMusic.mp3'
        fullpath = os.path.join(os.getcwd(), filepath)
        url = QtCore.QUrl.fromLocalFile(fullpath)
        self.__content = QtMultimedia.QMediaContent(url)

        self.__runner = threading.Thread(target=self.startGame)
        self.__runner.start()

    def createLCD(self):
        myLCD_style = """
            QLCDNumber {
                background-color: rgb(0, 0, 0);
                border: 2px solid rgb(113, 113, 113);
                border-width: 2px;
                border-radius: 15px;
                color: rgb(42, 232, 35);
            }
        """
        enemyLCD_style = """
            QLCDNumber {
                background-color: rgb(0, 0, 0);
                border: 2px solid rgb(113, 113, 113);
                border-width: 2px;
                border-radius: 15px;
                color: rgb(232, 35, 35);
            }
        """
        timeLCD_style = """
            QLCDNumber {
                background-color: rgb(0, 0, 0);
                border: 2px solid rgb(113, 113, 113);
                border-width: 2px;
                border-radius: 20px;
                color: rgb(255, 255, 255);
            }
        """
        self.__timeLCD = QLCDNumber(self)
        self.__timeLCD.setGeometry(QRect(560, 55, 200, 100)) #(QRect(580, 55, 140, 100))
        self.__timeLCD.setStyleSheet(timeLCD_style)
        self.__enemyScoreLCD = QLCDNumber(self)
        self.__enemyScoreLCD.setGeometry(QRect(900, 80, 140, 70))
        self.__enemyScoreLCD.setStyleSheet(enemyLCD_style)
        self.__myScoreLCD = QLCDNumber(self)
        self.__myScoreLCD.setGeometry(QRect(270, 80, 140, 70))
        self.__myScoreLCD.setStyleSheet(myLCD_style)

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
            self.__musicPlayer.setMedia(self.__content)
            # self.__musicplayer.setVolume(50.0)
            self.__musicPlayer.play()
        except Exception as e:
            print('error in startGame():', e)

    def __action(self):
        if self.__status == 2:   # game ended
            data = 'final\n' + str(self.__myScore) + '\n'
            try:
                self.__net.sendData(data)
            except:
                pass
            self.__musicPlayer.stop()
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
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio) #(640,480) #
            self.changePixmapItem.emit(p)
            self.__CFIRunner = threading.Timer(0.04, self.__convertFaceImage)
            self.__CFIRunner.start()

    @pyqtSlot(QImage)
    def setFaceImage(self, image):
        self.__faceImage.setPixmap(QPixmap.fromImage(image))
        self.setResult(self.__camera.state)

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
        if int(self.__elapseTime) >= self.duration:
            self.__status = 2

            return
        self.__displayTimeRunner = threading.Timer(1, self.__displayTime)
        self.__displayTimeRunner.start()

    @pyqtSlot()
    def __displayTimeAction(self):
        self.__timeLCD.display(self.duration - int(self.__elapseTime))

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
        if self.__myScore > self.__enemyScore: # win
            pixmap = QPixmap("resources/win.png")
            QGPI = QGraphicsPixmapItem()
            QGPI.setPixmap(pixmap)
            QGPI.setPos(150, 160)
            self.__scene.addItem(QGPI)

        elif self.__myScore < self.__enemyScore: # lose
            pixmap = QPixmap("resources/lose.png")
            QGPI = QGraphicsPixmapItem()
            QGPI.setPixmap(pixmap)
            QGPI.setPos(100, 160)
            self.__scene.addItem(QGPI)
        else:
            pixmap = QPixmap("resources/tie.png")
            QGPI = QGraphicsPixmapItem()
            QGPI.setPixmap(pixmap)
            QGPI.setPos(150, 160)
            self.__scene.addItem(QGPI)
        if hasattr(self, '_GamePage__actioner'):
            self.__actioner.cancel()
        if hasattr(self, '_GamePage__renderEmojiRunner'):
            self.__renderEmojiRunner.cancel()
        if hasattr(self, '_GamePage__displayTimeRunner'):
            self.__displayTimeRunner.cancel()
        if hasattr(self, '_GamePage__CFIRunner'):
            self.__CFIRunner.cancel()
        self.__camera.stop()
        self.__camera.release()
        if hasattr(self.__camera, 'captureThread'):
            self.__camera.captureThread.cancel()
        if hasattr(self.__camera, 'predictThread'):
            self.__camera.predictThread.cancel()
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
        
        if hasattr(self, '_GamePage__CFIRunner'):
            self.__CFIRunner.cancel()
        self.__camera.stop()
        self.__camera.release()
        if hasattr(self.__camera, 'captureThread'):
            self.__camera.captureThread.cancel()
        if hasattr(self.__camera, 'predictThread'):
            self.__camera.predictThread.cancel()
        
        try:
            self.__net.close()
        except:
            pass
        event.accept()
