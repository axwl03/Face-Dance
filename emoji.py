from PyQt5 import QtCore, QtGui

class Emoji:
    NONE = 0
    ANGRY = 1
    HAPPY = 2
    SAD = 3
    SURPRISE = 4

    def __init__(self, x, y, emojiType):
        self.__x = x
        self.__y = y
        self.__type = emojiType
        self.__status = 0   # 0: new, 1: exist, 2: out

    def getPic(self):
        return {
                0:'none',
                1:QtGui.QPixmap('resources/angry.png'),
                2:QtGui.QPixmap('resources/happy.png'),
                3:QtGui.QPixmap('resources/sad.png'),
                4:QtGui.QPixmap('resources/surprise.png')
            }.get(self.__type, "Invalid")

    def getStatus(self):
        return self.__status

    def getX(self):
        return self.__x

    def getY(self):
        return self.__y

    def getType(self):
        return self.__type
        
    def setStatus(self, status):
        self.__status = status

    def setX(self, x):
        self.__x = x

    def setY(self, y):
        self.__y = y

    def setType(self, emojiType):
        self.__type = emojiType

    def toString(self):
        return '{} {} {}'.format(self.__x, self.__y, self.__type)

    @staticmethod
    def parseString(string):
        data = string.split()
        return Emoji(data[0], data[1], data[2])