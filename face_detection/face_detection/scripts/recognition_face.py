import cv2
import os
import numpy
import base64
import requests
import json
from django.conf import settings
from face_detection.app.models import Cameras
from face_detection.app.tasks import set_notifications

def run():
    dir_faces = os.path.join(settings.MEDIA_ROOT, 'att_faces/orl_faces')
    size = 4

    # Crear una lista de imagenes y una lista de nombres correspondientes
    (images, lables, names, id) = ([], [], {}, 0)
    for (subdirs, dirs, files) in os.walk(dir_faces):
        for subdir in dirs:
            names[id] = subdir
            subjectpath = os.path.join(dir_faces, subdir)
            for filename in os.listdir(subjectpath):
                path = subjectpath + '/' + filename
                lable = id
                images.append(cv2.imread(path, 0))
                lables.append(int(lable))
            id += 1
    (im_width, im_height) = (112, 92)

    # Crear una matriz Numpy de las dos listas anteriores
    (images, lables) = [numpy.array(lis) for lis in [images, lables]]
    # OpenCV entrena un modelo a partir de las imagenes
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(images, lables)


    xml_file = os.path.join(settings.APPS_DIR, 'fixtures/haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(xml_file)
    cameradb = Cameras.objects.filter(is_active=True)

    while True:
        for camera in cameradb:
            response = requests.get("http://localhost:8000/frame/video/{}/".format(camera.pk))
            data = response.json()
            frame = json.loads(data)
            if not frame == "error":
                frame = numpy.asarray(frame["frame"], dtype=numpy.uint8)
                frame=cv2.flip(frame,1,0)

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

                    # Intentado reconocer la cara
                    prediction = model.predict(face_resize)
                    
                    #Dibujamos un rectangulo en las coordenadas del rostro
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    
                    # Escribiendo el nombre de la cara reconocida
                    # La variable cara tendra el nombre de la persona reconocida
                    cara = '%s' % (names[prediction[0]])

                    #Si la prediccion tiene una exactitud menor a 100 se toma como prediccion valida
                    if prediction[1]<100 :
                        #Ponemos el nombre de la persona que se reconoció
                        cv2.putText(frame,'%s - %.0f' % (cara,prediction[1]),(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
                      
                        retval, buffer = cv2.imencode('.png', frame)
                        png_as_text = base64.b64encode(buffer).decode('ascii')
                        #png_original = base64.b64decode(jpg_as_text).decode('ascii')
                        set_notifications(cara, camera.pk, png_as_text)
                        #En caso de que la cara sea de algun conocido se realizara determinadas accione          
                          

                    #Si la prediccion es mayor a 100 no es un reconomiento con la exactitud suficiente
                    elif prediction[1]>101 and prediction[1]<500:           
                        #Si la cara es desconocida, poner desconocido
                        cv2.putText(frame, 'Desconocido',(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))  

                    #Mostramos la imagen
                    #cv2.imshow('OpenCV Reconocimiento facial', frame)

                    #Si se presiona la tecla ESC se cierra el programa
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyAllWindows()
            break
