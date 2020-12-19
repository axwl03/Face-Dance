from PyQt5.QtWidgets import QApplication, QWidget
from startMenu import Ui_Form
from connectionCtrl import SecondPage
import sys

class MainPage(QWidget):
    def __init__(self):
        super(MainPage, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.iniGuiEvent()

    def iniGuiEvent(self):
        self.ui.pushButton.clicked.connect(self.jumpPage)
        self.ui.pushButton_2.clicked.connect(self.closescr)

    def jumpPage(self):
        self.nextPage = SecondPage()
        mainPage.hide()
        self.nextPage.show()

    def closescr(self):
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)    
    mainPage = MainPage()
    mainPage.show()
    sys.exit(app.exec_())
