from PyQt5.QtWidgets import QApplication, QWidget
from gamePage import Ui3_Form
from netModule import NetModule
import threading
from emoji import Emoji

class ThirdPage(QWidget):
    def __init__(self, isServer, ip):
        super(ThirdPage, self).__init__()
        self.ui = Ui3_Form()
        self.ui.setupUi(self)
        self.isServer = isServer
        self.ip = ip
        self.ui.label.setText(str(self.ip))

        self.__matchedEmoji = Emoji.NONE
        self.__faceImage = None
        self.__emojiList = []
        self.__myEmojiList = []
        self.__port = 8080

        self.__net = NetModule(self)
        self.__runner = threading.Thread(target=self.startGame)
        self.__runner.start()

    def startGame(self):
        if self.isServer == True:
            self.__net.listen(self.__port)
        else:
            self.__net.connect(self.ip, self.__port)

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
    def setFaceImage(self, faceImage):
        self.__faceImage = faceImage