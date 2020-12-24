from PyQt5.QtWidgets import QApplication, QWidget
from gamePage import Ui3_Form
from netModule import NetModule
import threading
from emoji import Emoji
import random
import time

class ThirdPage(QWidget):
    maxEmojiNum = 8
    maxEmojiGen = 1
    maxX = 450
    maxY = 500
    myOffsetX = 500
    myOffsetY = 200
    duration = 30

    def __init__(self, isServer, ip):
        super(ThirdPage, self).__init__()
        self.ui = Ui3_Form()
        self.ui.setupUi(self)
        self.isServer = isServer
        self.ip = ip
        self.ui.label.setText(str(self.ip))
        self.__myScore = 0
        self.__enemyScore = 0

        self.__matchedEmoji = Emoji.NONE
        self.__faceImage = None
        self.__emojiList = []
        self.__myEmojiList = []
        self.__port = 8080

        self.__net = NetModule(self)
        self.__mutex = threading.Lock()

        # TODO: this should be called after start button has been
        # clicked and is in the slot for the start button clicked signal
        self.__runner = threading.Thread(target=self.startGame)
        self.__runner.start()

    def startGame(self):

        # TODO: the code to establish connection should move into 
        # contructor before the start button is enabled
        if self.isServer == True:
            self.__net.listen(self.__port)
        else:
            self.__net.connect(self.ip, self.__port)
        
        startTime = time.time()
        if self.isServer == True:
            while True:
                msg = input()
                self.__action()
                if msg == 'exit':
                    self.__net.close()
                    break

    # TODO: this function should move into startGame function
    def __action(self):
        if self.isServer == True:
            # remove emoji if it exceeds boundary + 20
            i = 0
            while i < len(self.__myEmojiList):
                if self.__myEmojiList[i].getY() > self.maxY + self.myOffsetY + 20:
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
            # remove emoji if it exceeds boundary + 20
            i = 0
            while i < len(self.__myEmojiList):
                if self.__myEmojiList[i].getY() > self.maxY + self.myOffsetY + 20:
                    del self.__myEmojiList[i]
                    continue
                i = i + 1

            # send score to enemy
            data = 'score\n' + str(self.__myScore) + '\n'
            self.__net.sendData(data)

    # set result that predicted by image module
    def setResult(self, emojiType):
        self.__matchedEmoji = emojiType

    # set face image which is obtained from webcam
    def setFaceImage(self, faceImage):
        self.__faceImage = faceImage

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
