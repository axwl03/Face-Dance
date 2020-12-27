from PyQt5.QtWidgets import QApplication
import sys

from startMenuPage import StartMenuPage

if __name__ == '__main__':
    app = QApplication(sys.argv)    
    startMenuPage = StartMenuPage()
    startMenuPage.show()
    sys.exit(app.exec_())