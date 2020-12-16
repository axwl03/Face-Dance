from PyQt5.QtWidgets import QApplication, QWidget
from connectionSetup import Ui2_Form
from gameCtrl import ThirdPage

class SecondPage(QWidget):
    def __init__(self):
        super(SecondPage, self).__init__()
        self.ui = Ui2_Form()
        self.ui.setupUi(self) # self = Form
        self.iniGuiEvent()

    def iniGuiEvent(self):
        self.ui.pushButton.clicked.connect(self.chooseServer)
        self.ui.pushButton_2.clicked.connect(self.chooseClient)

    def chooseServer(self):
        self.isServer = 1
        self.nextPage = ThirdPage(self.isServer, -1)
        self.hide()
        self.nextPage.show()

    def chooseClient(self):
        self.isServer = 0
        self.ip = self.ui.lineEdit.text() #QString
        self.nextPage = ThirdPage(self.isServer, self.ip)
        self.hide()
        self.nextPage.show()
