import socket
import struct
import netifaces as ni
import threading
import time
from emoji import Emoji

class NetModule:
    def __init__(self, ui):
        self.ui = ui
        self.__isServer = False
        self.__listening = False

    def isServer(self):
        return self.__isServer

    @staticmethod
    def getLocalAddress():
        return ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    
    def connect(self, ip, port):
        self.__isServer = False
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ip == '':
            ip = '127.0.0.1'
        self.__socket.connect((ip, port))
        print('Connected')
        self.__listener = threading.Thread(target=self.__run)
        self.__listener.start()

    def listen(self, port):
        self.__isServer = True
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind(('', port))
        self.__listening = True
        self.__serverSocket.listen(1)
        print('listening')
        self.__socket, addr = self.__serverSocket.accept()
        self.__listener = threading.Thread(target=self.__run)
        self.__listener.start()
        self.__serverSocket.close()

    def __run(self):
        try:
            while True:
                msgType = self.recv(1)
                print('msgType = ' + msgType)
                if msgType == 'e':
                    break
                elif msgType == 'd':    # data
                    length = int.from_bytes(self.recv(4, True), byteorder='little')
                    data = self.recv(length)
                    print('Data = ' + data)
                    self.__handleData(data)
            self.__socket.close()
        except Exception as e:
            print('error in NetModule.__run():', e)
        print('connection closed')

    def __handleData(self, data):
        data = data.rstrip().split('\n')
        if data[0] == 'new':
            for emojiData in data[1:]:
                emoji = Emoji.parseString(emojiData)
                emoji.setX(emoji.getX() + self.ui.myOffsetX)
                emoji.setY(emoji.getY() + self.ui.myOffsetY)
                self.ui.myEmojiAdd(emoji)
        elif data[0] == 'score':
            self.ui.setEnemyScore(int(data[1]))
        elif data[0] == 'final':
            self.ui.setEnemyScore(int(data[1]))
            self.ui.gameEnd.emit()

    def send(self, data, isByte=False):
        totalsent = 0
        while totalsent < len(data):
            if isByte == False:
                sent = self.__socket.send(bytes(data[totalsent:], 'utf-8'))
            else:
                sent = self.__socket.send(data[totalsent:])
            if sent == 0:
                raise RuntimeError('send failed')
            totalsent = totalsent + sent
            print('sent: {}, totalsent: {}'.format(str(sent), str(totalsent)))

    def sendData(self, data):
        self.send('d')
        length = len(data).to_bytes(4, byteorder='little')
        self.send(length, True)
        self.send(data)

    def recv(self, length, isByte=False):
        data = b''
        totalrecd = 0
        while totalrecd < length:
            recd = self.__socket.recv(length - totalrecd)
            if len(recd) == 0:
                raise RuntimeError('recv failed')
            totalrecd = totalrecd + len(recd)
            data = data + recd
            print('recd: {}, totalrecd: {}'.format(str(len(recd)), str(totalrecd)))
        if isByte == False:
            return data.decode('utf-8')
        else:
            return data
    
    def close(self):
        self.send('e')
        self.__socket.close()

    def stopListen(self):
        self.__serverSocket.close()
        self.__listening = False

    def isListening(self):
        return self.__listening