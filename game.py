from PyQt5.QtWidgets import QApplication, QWidget
from gamePage import Ui3_Form

class ThirdPage(QWidget):
    def __init__(self, isServer, ip):
        super(ThirdPage, self).__init__()
        self.ui = Ui3_Form()
        self.ui.setupUi(self)
        self.isServer = isServer
        self.ip = ip
        self.ui.label.setText(str(self.ip))
