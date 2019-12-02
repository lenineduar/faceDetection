import cv2
import os
import numpy
import sys
from django.conf import settings
from utils.camera import CameraStream
from face_detection.app.models import Cameras
from face_detection.app.utils import replace_special_character

def run(*args):
    nombre = input('Introduzca el nombre: ')
    if not nombre == '':
        nombre = replace_special_character(nombre)
        dir_faces = os.path.join(settings.MEDIA_ROOT, 'att_faces/orl_faces')
        path = os.path.join(dir_faces, nombre.replace(" ","_"))

        #Tamaño para reducir a miniaturas las fotografias
        size = 4

        #Si no hay una carpeta con el nombre ingresado entonces se crea
        if not os.path.isdir(path):
            os.mkdir(path)

        #cargamos la plantilla e inicializamos la webcam
        xml_file = os.path.join(settings.APPS_DIR, 'fixtures/haarcascade_frontalface_default.xml')
        face_cascade = cv2.CascadeClassifier(xml_file)

        cameradb = Cameras.objects.filter(is_active=True).first()

        cap = CameraStream(cameradb.src)

        img_width, img_height = 112, 92

        #Ciclo para tomar fotografias
        count = 0
        while count < 100:
            #leemos un frame y lo guardamos
            img = cap.read()
            img = cv2.flip(img, 1, 0)

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
                cv2.putText(img, nombre, (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))        

                #El nombre de cada foto es el numero del ciclo
                #Obtenemos el nombre de la foto
                #Despues de la ultima sumamos 1 para continuar con los demas nombres
                pin=sorted([int(n[:n.find('.')]) for n in os.listdir(path)
                       if n[0]!='.' ]+[0])[-1] + 1

                #Metemos la foto en el directorio
                cv2.imwrite('%s/%s.png' % (path, pin), face_resize)

                #Contador del ciclo
                count += 1

            #Mostramos la imagen
            cv2.imshow('OpenCV Entrenamiento de '+nombre, img)

            #Si se presiona la tecla ESC se cierra el programa
            key = cv2.waitKey(10)
            if key == 27:
                cv2.destroyAllWindows()
                cap.stop()
                break
        cap.stop()
    else:
        print ("Se requiere nombre del sujeto")