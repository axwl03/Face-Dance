from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont

import sys

from connectionSetupPage import ConnectionSetupPage
from imageModule import ImgModule


class StartMenuPage(QWidget):
    def __init__(self):
        self.__WIDTH = 350
        self.__HEIGHT = 400
        self.__font = QFont()
        self.__font.setFamily("Comic Sans MS")
        super(StartMenuPage, self).__init__()
        self.resize(self.__WIDTH, self.__HEIGHT)
        self.setWindowTitle("Start Menu")
        
        self.camera = ImgModule()
        self.camera.loadModelThread.start()

        self.createLabel()
        self.createBtn()

    def createLabel(self):
        self.__font.setPointSize(30)

        self.__label = QLabel("Face Dance", self)
        self.__label.setGeometry(QRect(45, 30, 271, 81))
        self.__label.setFont(self.__font)

        self.__label2 = QLabel("Challenge", self)
        self.__label2.setGeometry(QRect(70, 90, 241, 81))
        self.__label2.setFont(self.__font)
        
    def createBtn(self):
        self.__font.setPointSize(15)

        btn = QPushButton("Play", self)
        btn.setGeometry(QRect(130, 230, 111, 51))
        btn.setFont(self.__font)
        btn.clicked.connect(self.jumpPage)

        btn2 = QPushButton("Exit", self)
        btn2.setGeometry(QRect(130, 300, 111, 51))
        btn2.setFont(self.__font)
        btn2.clicked.connect(self.closeScr)

    def jumpPage(self):
        self.__nextPage = ConnectionSetupPage(self.camera)
        self.hide()
        self.__nextPage.show()

    def closeScr(self):
        sys.exit()