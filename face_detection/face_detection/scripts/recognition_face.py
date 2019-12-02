import cv2
import os
import dlib
import cvlib as cv
from django.conf import settings
from threading import Thread
from face_detection.app.models import Cameras
from utils.prediction import (
    prediction, prediction_fd, landmarks_to_np, get_centers, get_aligned_face,
    judge_eyeglass)
from utils.camera import CameraStream

def run():
    size = 4
    (im_width, im_height) = (112, 92)
    
    # Cargo el archivo de configuración para la detección de rostros
    xml_file = os.path.join(settings.APPS_DIR,
        'fixtures/haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(xml_file)
    predictor_eye_path = os.path.join(settings.APPS_DIR,
        'fixtures/shape_predictor_5_face_landmarks.dat')
    detector = dlib.get_frontal_face_detector()
    predictor_eye = dlib.shape_predictor(predictor_eye_path)
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

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
                mini = cv2.resize(frame, (int(frame.shape[1] / size), int(frame.shape[0] / size)))

                """buscamos las coordenadas de los rostros (si los hay) y
                guardamos su posicion"""
                faces, confidence = cv.detect_face(mini)
                for i, f in enumerate(faces):
                    (startX, startY) = size*f[0], size*f[1]
                    (endX, endY) = size*f[2], size*f[3]

                    face = gray[startY:endY,startX:endY]
                    face_ok = False
                    try:
                        face_ok = True if (len(face[0]) > 0 and len(face) > 0) else False
                    except:
                        pass

                    if face_ok:
                        face_resize = cv2.resize(face, (im_width, im_height))
                        cv2.rectangle(frame, (startX, startY), (endX,endY), (0,0,255), 3)
                        
                        #*****************************Reconocimiento de lentes***********************************
                        '''rects = detector(gray, 1)

                        for i, rect in enumerate(rects):
                            x_face = rect.left()
                            y_face = rect.top()
                            w_face = rect.right() - x_face
                            h_face =  rect.bottom() - y_face
                    
                            landmarks = predictor_eye(gray,rect)
                            landmarks = landmarks_to_np(landmarks)
                            for (x, y) in landmarks:
                                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                
                            LEFT_EYE_CENTER, RIGHT_EYE_CENTER = get_centers(frame, landmarks)
                    
                            aligned_face = get_aligned_face(gray, LEFT_EYE_CENTER, RIGHT_EYE_CENTER)
                    
                            judge = judge_eyeglass(aligned_face)
                            if judge == True:
                                cv2.putText(frame, "Usando Lentes",
                                    (x_face + 100, y_face - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2, cv2.LINE_AA)
                            else:
                                continue'''


                        # Se realiza la predección
                        #prediction(face_resize, cap["camera_id"], frame)
                        name, prediction = prediction_fd(face_resize, cap["camera_id"], frame)

                        cara = '%s' % (name)
                        text = "{:.2f}%".format(confidence[i]*100)
                        if prediction[1]<=130: #Rostro identificado
            #                #Dibujamos un rectangulo en las coordenadas del rostro
            #            #Ponemos el nombre de la persona que se reconoció
                            cv2.putText(frame,'%s' % (cara),(startX+20,startY-10),cv2.FONT_HERSHEY_PLAIN,2,(0, 255, 255))
                            cv2.putText(frame,text,(endX-20,startY-10),cv2.FONT_HERSHEY_PLAIN,2,(0, 255, 255))
                              
            #    #        #Si la prediccion es mayor a 100 no es un reconomiento con la exactitud suficiente
                        else:#if #prediction[1]>101 and prediction[1]<500: 
                            cv2.putText(frame, 'Desconocido',(startX+20,startY-10), cv2.FONT_HERSHEY_PLAIN,1,(0,0,255))
                            
                    #Mostramos la imagen
                #cv2.imshow('OpenCV Reconocimiento facial', frame)

        #Si se presiona la tecla ESC se cierra el programa
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyAllWindows()
            for cap in cameras:
                cap["src"].stop()
            break
