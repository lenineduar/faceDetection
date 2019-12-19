import cv2
import os
import numpy
import sys
import base64
import pickle
import json
import mimetypes
from django.views.decorators import gzip
from django.shortcuts import render, redirect
from utils.camera import CameraStream
from utils.cameras_discovery import discovery
from django.views.generic import View
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from braces.views import LoginRequiredMixin
from django.conf import settings

from .utils import replace_special_character
from .models import Cameras

'''
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
'''

person_name = ''
cap = None
count = 0
path = ''

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


# -------------------------------------------------------
# Stream Section
# -------------------------------------------------------
def init_capture(camara_id, nombre):
    global count
    global cap
    global person_name
    global path

    person_name = replace_special_character(nombre)

    dir_faces = os.path.join(settings.MEDIA_ROOT, 'att_faces/orl_faces')
    path = os.path.join(dir_faces, person_name.replace(" ","_"))

    #Si no hay una carpeta con el nombre ingresado entonces se crea
    if not os.path.isdir(path):
        os.mkdir(path)
    cameradb = Cameras.objects.filter(pk=camara_id).first()
    cap = CameraStream(cameradb.src)

    #Ciclo para tomar fotografias 
    count = 0


def get_capture_frame():
    global count
    global cap
    global person_name
    global path
    #Tamaño para reducir a miniaturas las fotografias
    size = 4
    img_width, img_height = 112, 92
    #cargamos la plantilla e inicializamos la webcam
    xml_file = os.path.join(settings.APPS_DIR, 'fixtures/haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(xml_file)
    while count < 100:
        #leemos un frame y lo guardamos
        img = cap.read()
        #img = cv2.flip(img, 1, 0)

        #convertimos la imagen a blanco y negro
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
        #redimensionar la imagen
        mini = cv2.resize(gray, (int(gray.shape[1] / size), int(gray.shape[0] / size)))

        """buscamos las coordenadas de los rostros (si los hay) y
        guardamos su posicion"""
        faces = face_cascade.detectMultiScale(mini)    
        faces = sorted(faces, key=lambda x: x[3])

        if faces:
            face_i = faces[0]
            (x, y, w, h) = [v * size for v in face_i]
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (img_width, img_height))

            #Dibujamos un rectangulo en las coordenadas del rostro
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            #Ponemos el nombre en el rectagulo
            cv2.putText(img, person_name, (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))        

            #El nombre de cada foto es el numero del ciclo
            #Obtenemos el nombre de la foto
            #Despues de la ultima sumamos 1 para continuar con los demas nombres
            pin=sorted([int(n[:n.find('.')]) for n in os.listdir(path)
                if n[0]!='.' ]+[0])[-1] + 1

            #Metemos la foto en el directorio
            cv2.imwrite('%s/%s.png' % (path, pin), face_resize)

            #Contador del ciclo
            count += 1
        
        convert = cv2.imencode('.jpg', img)[1].tobytes()
        #Mostramos la imagen
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n')

    cap.stop()
    image_path = os.path.join(
        settings.ROOT_DIR,
        "face_detection\static\images\success_1.png"
    )
    image_mimetype = mimetypes.MimeTypes().guess_type(image_path)[0]
    image_data = open(image_path, "rb").read()
    yield (b'--frame\r\n'
            b'Content-Type: image/png\r\n\r\n' + image_data + b'\r\n')

def VideoStreamingCaptureView(request):
    return StreamingHttpResponse(get_capture_frame(),
        content_type='multipart/x-mixed-replace; boundary=frame')
