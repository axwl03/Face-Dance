import cv2
import time
import threading
from tensorflow import keras, Graph, Session
import tensorflow as tf
import numpy as np


class ImgModule:
    def __init__(self):
        
        self.__cap = cv2.VideoCapture(0)
        self.__interval = 0.03 # 30ms
        self.__emotionMap = {0: 'None', 1: 'Angry', 2: 'Happy', 3: 'Sad', 4: 'Surprise'}
        # self.__emotionMap = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5:'Surprise', 6:'None'}

        self.__model = None
        self.__thread_graph = None
        self.__thread_session = None
        self.__graph = None

        self.loadModelThread = threading.Thread(target=self.load)

        self.__lock = threading.Lock()
        self.__lock2 = threading.Lock()

        self.frame = np.array([]) # for setFaceImage
        self.state = 'None'# for setResult

        self.__inputImg = None
        self.__capLegal = True
        self.__predictLegal = False
        self.__writeLegal = True 

    def load(self):
        print('loading....')
        self.__thread_graph = Graph()
        with self.__thread_graph.as_default():
            self.__thread_session = Session()
            with self.__thread_session.as_default():
                self.__model = keras.models.load_model('weights-28-0.77.h5', compile=False)
                self.__graph = tf.compat.v1.get_default_graph()
                self.__predictLegal = True
                print('loading done.')
        return self.__model, self.__graph, self.__thread_session
    

    def capture(self):
        self.__lock.acquire()
        if(self.__capLegal):
            ret, img = self.__cap.read()
            self.__lock.release()
            if(ret == True):
                self.frame = img
                img = cv2.cvtColor(cv2.resize(img, (48, 48)), cv2.COLOR_BGR2GRAY)
                if(self.__writeLegal):
                    self.__inputImg = np.reshape(img, (1, 48, 48, 1)) / 255.0
            else:
                print('Error in img capture')
        else:
            self.__lock.release()
        self.captureThread = threading.Timer(0.04, self.capture)
        self.captureThread.start()

    def predict(self):
        self.__lock2.acquire()
        if(self.__predictLegal):
            self.__lock2.release()
            self.__writeLegal = False
            with self.__graph.as_default():
                with self.__thread_session.as_default():
                    self.state = self.__model.predict_classes(self.__inputImg)[0]
            
            print('res : {}'.format(self.__emotionMap[self.state]))

            self.__writeLegal = True
            # time.sleep(self.__interval)
        else:
            self.__lock2.release()
        self.predictThread = threading.Timer(1, self.predict)
        self.predictThread.start()

    def setFPS(self, f):
        if(f <= 100 and f > 0):
            self.__interval = 1 / f
        elif(f <= 0):
            print('FPS should be >= 0!')
            self.__interval = 1
        else:
            print('FPS should be <= 100!')
            self.__interval = 100

    def release(self):
        self.__cap.release()
    
    def stop(self):
        self.__lock.acquire()
        self.__capLegal = False
        # self.__predictLegal = False
        self.__lock.release()

    def reset(self):
        self.__capLegal = True
        self.__predictLegal = True

#imgModule = ImgModule()
#imgModule.start()