import socket
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
        self.__listener = threading.Thread(target=self.run)
        self.__listener.start()

    def listen(self, port):
        self.__isServer = True
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind(('', port))
        self.__serverSocket.listen(1)
        print('listening')
        self.__socket, addr = self.__serverSocket.accept()
        self.__listener = threading.Thread(target=self.run)
        self.__listener.start()
        self.__serverSocket.close()

    def run(self):
        while True:
            msgType = self.recv(1)
            print('msgType = ' + msgType)

    def send(self, data):
        totalsent = 0
        while totalsent < len(data):
            sent = self.__socket.send(bytes(data[totalsent:], 'utf-8'))
            if sent == 0:
                raise RuntimeError('send failed')
            totalsent = totalsent + sent
            print('sent: {}, totalsent: {}'.format(str(sent), str(totalsent)))

    def recv(self, length):
        data = ''
        totalrecd = 0
        while totalrecd < length:
            recd = self.__socket.recv(length - totalrecd)
            if len(recd) == 0:
                raise RuntimeError('recv failed')
            totalrecd = totalrecd + len(recd)
            data = data + recd.decode('utf-8')
            print('recd: {}, totalrecd: {}'.format(str(len(recd)), str(totalrecd)))
        return data
    
    def close(self):
        self.__socket.close()
        
mode = input() 
if mode == 's':
    net = NetModule('test')
    net.listen(8080)
    msgType = input()
    while True:
        if msgType != 'e':
            msg = input()
            net.send(msg)
        else:
            net.close()
            break
        msgType = input()
elif mode == 'c':
    net = NetModule('test')
    net.connect('127.0.0.1', 8080)
    msgType = input()
    while True:
        if msgType != 'e':
            msg = input()
            net.send(msg)
        else:
            net.close()
            break
        msgType = input()
