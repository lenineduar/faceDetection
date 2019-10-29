import cv2
import sys
import base64
import pickle
import json
from utils.camera import CameraStream
from django.views.generic import View
from django.http import StreamingHttpResponse, JsonResponse
from braces.views import LoginRequiredMixin
from django.conf import settings

from .models import Cameras


if sys.argv[1] == "runserver":
    cameras = []
    cameras.append(None)
    for i in range(1, settings.CAMERAS_ACTIVE+1):
        cameradb = Cameras.objects.filter(is_active=True, pk=i)
        if cameradb:
            src = int(cameradb[0].src) if cameradb[0].src == '0' else cameradb[0].src
            cam = CameraStream(src).start()
        else:
            cam = None

        cameras.append(cam)


def get_frame(cap):
        """Video streaming generator function."""
        while cap:
            frame = cap.read()
            convert = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n')

def recognition_frame(cap):
    frame = cap.read()
    return frame

# Streaming Section
def Video1StreamingView(request):
    if cameras[1]:
        return StreamingHttpResponse(get_frame(cameras[1]),
            content_type='multipart/x-mixed-replace; boundary=frame')

def Video2StreamingView(request):
    if cameras[2]:
        return StreamingHttpResponse(get_frame(cameras[2]),
            content_type='multipart/x-mixed-replace; boundary=frame')

def Video3StreamingView(request):
    if cameras[3]:
        return StreamingHttpResponse(get_frame(cameras[3]),
            content_type='multipart/x-mixed-replace; boundary=frame')

def Video4StreamingView(request):
    if cameras[4]:
        return StreamingHttpResponse(get_frame(cameras[4]),
            content_type='multipart/x-mixed-replace; boundary=frame')


def FrameVideo(resquest, camera):
    if cameras[int(camera)]:
        frame = recognition_frame(cameras[int(camera)])
        data = {
            'frame': frame.tolist(),
        }
    else:
        data = {
            'frame': "error",
        }
    data = json.dumps(data)
    return JsonResponse(data, safe=False)