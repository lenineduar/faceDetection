import cv2
import sys
import base64
import pickle
import json
from django.views.decorators import gzip
from utils.camera import CameraStream
from utils.cameras_discovery import discovery
from django.views.generic import View
from django.http import StreamingHttpResponse, JsonResponse
from braces.views import LoginRequiredMixin
from django.conf import settings

from .models import Cameras


if sys.argv[1] == "runserver":
    # discovery()
    cameras = []
    cameras.append(None)
    count = Cameras.objects.filter().count()
    for i in range(1, count+1):
        cameradb = Cameras.objects.filter(is_active=True, pk=1)
        if cameradb:
            src = int(cameradb[0].src) if cameradb[0].src == '0' else cameradb[0].src
            cam = CameraStream(
                src,
                width=settings.WIDTH_RES,
                height=settings.HEIGHT_RES)
        else:
            cam = None

        cameras.append(cam)


def get_frame(cap):
        """Video streaming generator function."""
        while cap:
            frame = cap.get_frame()
            # import pdb; pdb.set_trace()
            #frame = cap.read()
            #convert = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def recognition_frame(cap):
    frame = cap.read()
    return frame


# Streaming Section
@gzip.gzip_page
def Video1StreamingView(request):
    if cameras[1]:
        return StreamingHttpResponse(get_frame(cameras[1]),
            content_type='multipart/x-mixed-replace; boundary=frame')


@gzip.gzip_page
def Video2StreamingView(request):
    if cameras[2]:
        return StreamingHttpResponse(get_frame(cameras[2]),
            content_type='multipart/x-mixed-replace; boundary=frame')


@gzip.gzip_page
def Video3StreamingView(request):
    if cameras[3]:
        return StreamingHttpResponse(get_frame(cameras[3]),
            content_type='multipart/x-mixed-replace; boundary=frame')


@gzip.gzip_page
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