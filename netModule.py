import socket
import fcntl
import struct
import netifaces as ni
import threading
import time

class NetModule:
    def __init__(self, ui):
        self.ui = ui
        self.__isServer = False

    def isServer(self):
        return self.__isServer

    @staticmethod
    def getLocalAddress():
        return ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    
    def connect(self, ip, port):
        self.__isServer = False
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((ip, port))
        print('Connected')

#       self.__socket.sendall(b'Hello World')
#       self.__socket.close()

    def listen(self, port):
        self.__isServer = True
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind(('', port))
        self.__serverSocket.listen(1)
        self.__socket, addr = self.__serverSocket.accept()
        self.__listener = threading.Thread(target=self.run)
        self.__listener.start()
        self.__serverSocket.close()

#        print(self.__socket.recv(1024).decode('utf-8'))
#        self.__socket.close()

    def run(self):
        for i in range(5):
            print('listening')
            time.sleep(1)
        
mode = input() 
if mode == 's':
    net = NetModule('test')
    net.listen(8080)
elif mode == 'c':
    net = NetModule('test')
    net.connect('127.0.0.1', 8080)


