from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGraphicsDropShadowEffect, QVBoxLayout
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap

import sys

from connectionSetupPage import ConnectionSetupPage
#from imageModule import ImgModule


class StartMenuPage(QWidget):
    def __init__(self):
        self.__WIDTH = 460 #350 2048
        self.__HEIGHT = 500 #400 1365
        self.__font = QFont()
        self.__font.setFamily("Comic Sans MS")
        super(StartMenuPage, self).__init__()
        self.resize(self.__WIDTH, self.__HEIGHT)
        self.setWindowTitle("Start Menu")
        self.setObjectName("Form")
        
        #self.camera = ImgModule()
        #self.camera.loadModelThread.start()

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background.jpg")))
    
        self.setPalette(palette)
        self.createLabel()
        self.createBtn()

    def createLabel(self):
        # self.__font.setPointSize(30)
        self.__label = QLabel(self)
        self.__label.setGeometry(QRect(12, 0, 450, 150))
        self.__pixmap = QPixmap("resources/logo.png")
        self.__label.setPixmap(self.__pixmap)
        self.__label2 = QLabel(self)
        self.__label2.setGeometry(QRect(17, 80, 450, 150))
        self.__pixmap = QPixmap("resources/logo2.png")
        self.__label2.setPixmap(self.__pixmap)
        
    def createBtn(self):
        button_style = """
            QPushButton {
                border: 2px solid #ffffff;
                border-radius: 10px;
                background-color: #f0b41d;
                color: #000000;
                
                min-width: 80px;
            }
            
            QPushButton:hover {
                color: #ffffff;
                background-color: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                                  stop: 0 #000000, stop: 1 #00aaff);
            }
            
            QPushButton:pressed {
                background-color: #FFA823;
                color: #000000;
            }
        """

        self.__font.setPointSize(18)

        btn = QPushButton("Play", self)
        btn.setGeometry(QRect(160, 260, 120, 53))
        btn.setFont(self.__font)
        btn.setStyleSheet(button_style)
        btn.clicked.connect(self.jumpPage)

        btn2 = QPushButton("Exit", self)
        btn2.setGeometry(QRect(160, 350, 120, 53))
        btn2.setFont(self.__font)
        btn2.setStyleSheet(button_style)
        btn2.clicked.connect(self.closeScr)

    def jumpPage(self):
        #self.__nextPage = ConnectionSetupPage(self.camera)
        self.__nextPage = ConnectionSetupPage(None)
        self.hide()
        self.__nextPage.show()

    def closeScr(self):
        sys.exit()