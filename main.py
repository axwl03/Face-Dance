from PyQt5.QtWidgets import QApplication
from PyQt5 import QtMultimedia, QtCore

import sys, os

from startMenuPage import StartMenuPage

if __name__ == '__main__':
    app = QApplication(sys.argv)
    filepath = 'resources/color-X.mp3'
    fullpath = os.path.join(os.getcwd(), filepath)
    url = QtCore.QUrl.fromLocalFile(fullpath)
    content = QtMultimedia.QMediaContent(url)
    player = QtMultimedia.QMediaPlayer()
    player.setMedia(content)
    player.setVolume(50.0)
    player.play()
    startMenuPage = StartMenuPage(player)
    startMenuPage.show()
    sys.exit(app.exec_())