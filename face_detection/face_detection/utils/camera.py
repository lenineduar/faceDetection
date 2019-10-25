import os
import cv2
import mimetypes
from django.templatetags.static import static
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from threading import Thread, Lock
from django.conf import settings

class CameraStream(object):
   
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
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

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()


class VideoStreaming:
    def __init__(self):
        cv2.destroyAllWindows()
        self.camera = set_cameras(1)

    def __del__(self):
        if self.camera:
            self.camera.stop()

    def get(self, request, *args, **kwargs):
        """Video streaming route. Put this in the src attribute of an img tag."""
        if self.camera:
            return StreamingHttpResponse(self.get_frame(self.camera),
                content_type='multipart/x-mixed-replace; boundary=frame')

    def get_frame(self, cap):
        """Video streaming generator function."""
        while cap:
            frame = cap.read()
            convert = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n')