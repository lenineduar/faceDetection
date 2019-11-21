import os
import cv2
import mimetypes
from django.templatetags.static import static
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from threading import Thread, Lock
from django.conf import settings

<<<<<<< HEAD

class CameraStream(object):
    def __init__(self, src=0, width=None , height=None):
        self.video = cv2.VideoCapture(src)
        self.width = None
        self.height = None
        if width is not None and height is not None:
            self.video.set(3, width)
            self.video.set(4, height)
            self.width = width
            self.height = height
        (self.grabbed, self.frame) = self.video.read()
        Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        if self.width is not None and self.height is not None:
            image = cv2.resize(
                self.frame,(self.width, self.height),
                interpolation = cv2.INTER_CUBIC)
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

'''
class CameraStream(object):
   
    def __init__(self, src=0, width=None , height=None):
        self.stream = cv2.VideoCapture(src)
        if width is not None and height is not None:
            self.stream.set(3, width)
            self.stream.set(4, height)
=======
class CameraStream(object):
   
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
>>>>>>> 7bedb08bc860f6609aefc8928107001da37344cd
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()
        
    def start(self):
        if self.started:
            print("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
<<<<<<< HEAD
            frame = cv2.resize(frame,(160, 120), interpolation = cv2.INTER_CUBIC)
=======
>>>>>>> 7bedb08bc860f6609aefc8928107001da37344cd
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        self.thread.join()
        self.stream.release()

<<<<<<< HEAD
    def __del__(self):
        self.stop()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop()
'''
=======
    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()
>>>>>>> 7bedb08bc860f6609aefc8928107001da37344cd
