import cv2
import time
import threading
from tensorflow import keras, Graph, Session
import tensorflow as tf
import numpy as np


class ImgModule:
    def __init__(self):
        print('loading....')
        self.__cap = cv2.VideoCapture(0)
        self.__interval = 0.03 # 30ms
        self.__emotionMap = {0: 'None', 1: 'Angry', 2: 'Happy', 3: 'Sad', 4: 'Surprise'}
        # self.__emotionMap = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5:'Surprise', 6:'None'}

        self.__model = None
        self.__thread_graph = None
        self.__thread_session = None
        self.__graph = None

        self.__loadModelThread = threading.Thread(target=self.load)
        self.__captureThread = threading.Thread(target=self.capture)
        self.__predictThread = threading.Thread(target=self.predict)
        

        self.frame = None # for setFaceImage
        self.state = 'None'# for setResult


        self.__inputImg = None

        self.__capLegal = True
        self.__predictLegal = True
        self.__writeLegal = True
        print('loading done.')
    
    def start(self):
        self.__captureThread.start()
        self.__loadModelThread.start()
        time.sleep(3)
        # self.predict()
        self.__predictThread.start()

    def load(self):
        self.__thread_graph = Graph()
        with self.__thread_graph.as_default():
            self.__thread_session = Session()
            with self.__thread_session.as_default():
                self.__model = keras.models.load_model('weights-50-0.87.h5', compile=False)
                self.__graph = tf.compat.v1.get_default_graph()
        return self.__model, self.__graph, self.__thread_session
    

    def capture(self):
        while(self.__capLegal):
            ret, img = self.__cap.read()
            if(ret == True):
                self.frame = img
                img = cv2.cvtColor(cv2.resize(img, (48, 48)), cv2.COLOR_BGR2GRAY)
                if(self.__writeLegal):
                    self.__inputImg = np.reshape(img, (1, 48, 48, 1)) / 255.0
            else:
                print('Error in img capture')
    
    def predict(self):
        while(self.__predictLegal):
            self.__writeLegal = False

            with self.__graph.as_default():
                with self.__thread_session.as_default():
                    self.state = self.__model.predict_classes(self.__inputImg)[0]
            
            # print('res : {}'.format(self.__emotionMap[self.state]))

            self.__writeLegal = True
            time.sleep(self.__interval)

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
        self.__capLegal = False
        self.__predictLegal = False

    def reset(self):
        self.__capLegal = True
        self.__predictLegal = True

#imgModule = ImgModule()
#imgModule.start()



    
    


    
