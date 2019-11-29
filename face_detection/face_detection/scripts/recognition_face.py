import cv2
import os
from django.conf import settings
from threading import Thread
from face_detection.app.models import Cameras
from utils.prediction import prediction
from utils.camera import CameraStream

def run():
    size = 5
    (im_width, im_height) = (112, 92)
    
    # Cargo el archivo de configuración para la detección de rostros
    xml_file = os.path.join(settings.APPS_DIR, 'fixtures/haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(xml_file)

    # Obtengo de la base de datos las cámaras detectadas y activas
    cameras = list()
    cameradb = Cameras.objects.filter(is_active=True)
    # Exploro cada una de las cámaras y creo el hilo para el stream de la cámara
    for camera in cameradb:
        cap = {
            'src': CameraStream(camera.src),
            'camera_id': camera.id,
        }
        cameras.append(cap)

    while True:
        for cap in cameras:
                frame = cap["src"].read()            
                #frame=cv2.flip(frame,1,0)

                #convertimos la imagen a blanco y negro    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                #redimensionar la imagen
                mini = cv2.resize(gray, (int(gray.shape[1] / size), int(gray.shape[0] / size)))

                """buscamos las coordenadas de los rostros (si los hay) y
                guardamos su posicion"""
                faces = face_cascade.detectMultiScale(mini)
                for i in range(len(faces)):
                    face_i = faces[i]
                    (x, y, w, h) = [v * size for v in face_i]
                    face = gray[y:y + h, x:x + w]
                    face_resize = cv2.resize(face, (im_width, im_height))
                    
                    #Dibujamos un rectangulo en las coordenadas del rostro
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    
                    # Se realiza la predección
                    prediction(face_resize, cap["camera_id"], frame)
                    
                    #Mostramos la imagen
                #cv2.imshow('OpenCV Reconocimiento facial', frame)

        #Si se presiona la tecla ESC se cierra el programa
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyAllWindows()
            for cap in cameras:
                cap["src"].stop()
            break
