from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap

from gamePage import GamePage

class ConnectionSetupPage(QWidget):
    def __init__(self, camera, musicPlayer):
        self.__WIDTH = 350
        self.__HEIGHT = 350
        self.__font = QFont()
        self.__font.setFamily("Comic Sans MS")
        self.__font.setPointSize(12)
        super(ConnectionSetupPage, self).__init__()
        self.resize(self.__WIDTH, self.__HEIGHT)
        self.setWindowTitle("Connection Setup")
        self.setFixedSize(self.size())
        self.__lineEdit = QLineEdit(self)
        self.__lineEdit.setGeometry(QRect(48, 210, 240, 40))
        lineEdit_style = """
            QLineEdit {
                border: 2px solid rgb(37, 39, 48);
                border-radius: 20px;
                color: #FFF;
                padding-left: 20px;
                padding-right: 20px;
                background-color: rgb(34, 36, 44);
            }
            
            QLineEdit:hover {
                border: 2px solid rgb(48, 50, 62);
            }
            
            QLineEdit:focus {
                border: 2px solid rgb(85, 170, 255);
                background-color: rgb(43, 45, 56);
            }
        """
        self.__lineEdit.setPlaceholderText("Enter server IP")
        self.__lineEdit.setFont(self.__font)
        self.__lineEdit.setStyleSheet(lineEdit_style)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background2.jpg")))
        self.setPalette(palette)
        self.createBtn()

        self.camera = camera
        self.musicPlayer = musicPlayer
        self.__isServer = None
        self.__ip = None

    def createBtn(self):
        self.__font.setPointSize(17)

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

        btn = QPushButton("Server", self)
        btn.setGeometry(QRect(100, 60, 131, 53))
        btn.setFont(self.__font)
        btn.setStyleSheet(button_style)
        btn.clicked.connect(self.chooseServer)

        btn2 = QPushButton("Client", self)
        btn2.setGeometry(QRect(100, 145, 131, 53))
        btn2.setFont(self.__font)
        btn2.setStyleSheet(button_style)
        btn2.clicked.connect(self.chooseClient)

    def chooseServer(self):
        self.__isServer = 1
        self.__ip = -1
        self.__nextPage = GamePage(self.__isServer, self.__ip, self.camera, self.musicPlayer)
        self.hide()
        self.__nextPage.show()

    def chooseClient(self):
        self.__isServer = 0
        self.__ip = self.__lineEdit.text()
        self.__nextPage = GamePage(self.__isServer, self.__ip, self.camera, self.musicPlayer)
        self.hide()
        self.__nextPage.show()
