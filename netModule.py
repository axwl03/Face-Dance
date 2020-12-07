import socket
import fcntl
import struct
import netifaces as ni
import threading

class NetModule:
    def __init__(self, ui):
        self.ui = ui
        self.__serverSocket = None
        self.__clientSocket = None
        self.__isServer = False

    def isServer(self):
        return self.__isServer

    @staticmethod
    def getLocalAddress():
        return ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    
    def connect(self, ip, port):
        self.__isServer = False
        self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clientSocket.connect((ip, port))
        print('Connected')
        self.__clientSocket.sendall(b'Hello World')
        self.__clientSocket.close()

    def listen(self, port):
        self.__isServer = True
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind(('', port))
        self.__serverSocket.listen(1)
        conn, addr = self.__serverSocket.accept()
        print(conn.recv(1024).decode('utf-8'))
        self.__serverSocket.close()
        conn.close()

        
mode = input() 
if mode == 's':
    net = NetModule('test')
    net.listen(8080)
elif mode == 'c':
    net = NetModule('test')
    net.connect('127.0.0.1', 8080)


