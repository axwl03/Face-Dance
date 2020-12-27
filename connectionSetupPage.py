from PyQt5.QtWidgets import QWidget, QLabel, QPushButton,QLineEdit
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont

from gamePage import GamePage

class ConnectionSetupPage(QWidget):
    def __init__(self):
        self.__WIDTH = 341
        self.__HEIGHT = 311
        self.__font = QFont()
        self.__font.setFamily("Comic Sans MS")
        self.__font.setPointSize(15)
        super(ConnectionSetupPage, self).__init__()
        self.resize(self.__WIDTH, self.__HEIGHT)
        self.setWindowTitle("Connection Setup")
        
        self.__isServer = None
        self.__ip = None

        self.createBtn()
        self.__lineEdit = QLineEdit(self)
        self.__lineEdit.setGeometry(QRect(100, 180, 161, 31))
        self.__label = QLabel("ip: ", self)
        self.__label.setGeometry(QRect(60, 180, 31, 31))
        self.__label.setFont(self.__font)

    def createBtn(self):
        self.__font.setPointSize(15)

        btn = QPushButton("Server", self)
        btn.setGeometry(QRect(100, 60, 131, 41))
        btn.setFont(self.__font)
        btn.clicked.connect(self.chooseServer)

        btn2 = QPushButton("Client", self)
        btn2.setGeometry(QRect(100, 130, 131, 41))
        btn2.setFont(self.__font)
        btn2.clicked.connect(self.chooseClient)

    def chooseServer(self):
        self.__isServer = 1
        self.__ip = -1
        self.__nextPage = GamePage(self.__isServer, self.__ip)
        self.hide()
        self.__nextPage.show()

    def chooseClient(self):
        self.__isServer = 0
        self.__ip = self.__lineEdit.text()
        self.__nextPage = GamePage(self.__isServer, self.__ip)
        self.hide()
        self.__nextPage.show()
