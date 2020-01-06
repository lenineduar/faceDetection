#*************************Librerias**************************
from cv2 import cv2
from threading import Thread, Lock
import numpy as np
import time
import base64
import face_recognition
import dlib
import os
from utils.deteccion_gpu import clasificador
from django.conf import settings
from face_detection.app.models import Cameras
from face_detection.app.tasks import set_notifications
#************************************************************

class VideoStreamWidget(object):
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()
        self.start()
        
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

    def __del__(self):
        self.stop()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop()
    
    def get_aligned_face(self,img, left, right):
        desired_w = 256
        desired_h = 256
        desired_dist = desired_w * 0.5
        
        eyescenter = ((left[0]+right[0])*0.5 , (left[1]+right[1])*0.5)
        dx = right[0] - left[0]
        dy = right[1] - left[1]
        dist = np.sqrt(dx*dx + dy*dy)# 
        scale = desired_dist / dist # 
        angle = np.degrees(np.arctan2(dy,dx)) #
        M = cv2.getRotationMatrix2D(eyescenter,angle,scale)# 
    
        # update the translation component of the matrix
        tX = desired_w * 0.5
        tY = desired_h * 0.5
        M[0, 2] += (tX - eyescenter[0])
        M[1, 2] += (tY - eyescenter[1])
    
        aligned_face = cv2.warpAffine(img,M,(desired_w,desired_h))
        
        return aligned_face


    def landmarks_to_np(self,landmarks, dtype="int"):

        num = landmarks.num_parts
        
        # initialize the list of (x, y)-coordinates
        coords = np.zeros((num, 2), dtype=dtype)
        
        # loop over the 68 facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        for i in range(0, num):
            coords[i] = (landmarks.part(i).x, landmarks.part(i).y)
        # return the list of (x, y)-coordinates
        return coords

    def judge_eyeglass(self,img):
        img = cv2.GaussianBlur(img, (11,11), 0) 
    
        sobel_y = cv2.Sobel(img, cv2.CV_64F, 0 ,1 , ksize=-1) 
        sobel_y = cv2.convertScaleAbs(sobel_y) 
    
        edgeness = sobel_y 
        
        retVal,thresh = cv2.threshold(edgeness,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        d = len(thresh) * 0.5
        x = np.int32(d * 6/7)
        y = np.int32(d * 3/4)
        w = np.int32(d * 2/7)
        h = np.int32(d * 2/4)
    
        x_2_1 = np.int32(d * 1/4)
        x_2_2 = np.int32(d * 5/4)
        w_2 = np.int32(d * 1/2)
        y_2 = np.int32(d * 8/7)
        h_2 = np.int32(d * 1/2)
        
        roi_1 = thresh[y:y+h, x:x+w] 
        roi_2_1 = thresh[y_2:y_2+h_2, x_2_1:x_2_1+w_2]
        roi_2_2 = thresh[y_2:y_2+h_2, x_2_2:x_2_2+w_2]
        roi_2 = np.hstack([roi_2_1,roi_2_2])
        
        measure_1 = sum(sum(roi_1/255)) / (np.shape(roi_1)[0] * np.shape(roi_1)[1])
        measure_2 = sum(sum(roi_2/255)) / (np.shape(roi_2)[0] * np.shape(roi_2)[1])
        measure = measure_1*0.3 + measure_2*0.7
 
    
        if measure > 0.15:
            judge = True
        else:
            judge = False
        return judge

    def get_centers(self,img, landmarks):
        EYE_LEFT_OUTTER = landmarks[2]
        EYE_LEFT_INNER = landmarks[3]
        EYE_RIGHT_OUTTER = landmarks[0]
        EYE_RIGHT_INNER = landmarks[1]
    
        x = ((landmarks[0:4]).T)[0]
        y = ((landmarks[0:4]).T)[1]
        A = np.vstack([x, np.ones(len(x))]).T
        k, b = np.linalg.lstsq(A, y, rcond=None)[0]
        
        x_left = (EYE_LEFT_OUTTER[0]+EYE_LEFT_INNER[0])/2
        x_right = (EYE_RIGHT_OUTTER[0]+EYE_RIGHT_INNER[0])/2
        LEFT_EYE_CENTER =  np.array([np.int32(x_left), np.int32(x_left*k+b)])
        RIGHT_EYE_CENTER =  np.array([np.int32(x_right), np.int32(x_right*k+b)])
        
        #*******Quitar comentario para ver alineacion de ojos************
        # pts = np.vstack((LEFT_EYE_CENTER,RIGHT_EYE_CENTER))
        # cv2.polylines(img, [pts], False, (255,0,0), 1) 
        # cv2.circle(img, (LEFT_EYE_CENTER[0],LEFT_EYE_CENTER[1]), 3, (0, 0, 255), -1)
        # cv2.circle(img, (RIGHT_EYE_CENTER[0],RIGHT_EYE_CENTER[1]), 3, (0, 0, 255), -1)
        
        return LEFT_EYE_CENTER, RIGHT_EYE_CENTER
    
    def show_frame(self, camera_id):
        frame = self.frame
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mini = cv2.resize(frame, (int(frame.shape[1] / size), int(frame.shape[0] / size)))
        face_locations = face_recognition.face_locations(mini,number_of_times_to_upsample=1,model='cnn')
        face_encodings = face_recognition.face_encodings(mini, face_locations)
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top=size*top
            right=size*right
            left=size*left
            bottom=size*bottom
            # Busca coincidencias
            # Calibrar la tolerancia
            tolerancia=0.6
            matches = face_recognition.compare_faces(codificacion, face_encoding,tolerancia)

            name = "Desconocido"

            # Si se encontró una coincidencia en solo use la primera..
            if True in matches:
                first_match_index = matches.index(True)
                name = nombres[first_match_index]

            # O en su lugar, use la cara conocida con la menor distancia a la nueva cara
            face_distances = face_recognition.face_distance(codificacion, face_encoding)
            if face_distances:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = nombres[best_match_index]

            retval, buffer = cv2.imencode('.png', frame)
            png_as_text = base64.b64encode(buffer).decode('ascii')
            set_notifications(name, camera_id, png_as_text)


            # Dibuja un rectangulo alrededor del rostro
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Dibuja un rectangulo con el nombre (Quitar comentario para que aparezca en recuadro)
            cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            # Dibuja Nombre
            cv2.putText(frame, name, (left + 6, bottom + 20), font, 1.0, (255, 255, 255), 1)

            #***************************************Identifica si la persona usa lentes*******************************************
                   
            rect = dlib.rectangle(left,top, right,bottom)
            landmarks = predictor(gray, rect)
            landmarks = self.landmarks_to_np(landmarks)

            # Quitar comentario si se quiere ver marcas faciales
            #for (x, y) in landmarks:
            #    cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

            LEFT_EYE_CENTER, RIGHT_EYE_CENTER = self.get_centers(frame, landmarks)
                        
            aligned_face = self.get_aligned_face(gray, LEFT_EYE_CENTER, RIGHT_EYE_CENTER)
                       
            judge = self.judge_eyeglass(aligned_face)
            if judge == True:
                cv2.putText(frame, "Usa Lentes", (left + 100, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                #cv2.putText(frame, "Usa Lentes", (left + 100, top - 10), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255))
            # Quitar comentario si se desea que se muestre cuando la persona no usa lentes
            #else:
            #    cv2.putText(frame, "No Glasses", (left + 100, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255,0), 2, cv2.LINE_AA)

            #*********************************************************************************



        # Muestra imagen en pantalla
        #cv2.imshow('Reconocimiento facial',frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit(1)


#***************************************************************
def run():
    # Obtengo de la base de datos las cámaras detectadas y activas
    cameras = list()
    cameradb = Cameras.objects.filter(is_active=True)
    # Exploro cada una de las cámaras y creo el hilo para el stream de la cámara
    for camera in cameradb:
        cap = {
            'src': VideoStreamWidget(camera.src),
            'camera_id': camera.id,
        }
        cameras.append(cap)

    global size, codificacion, nombres, detector, predictor
    size=4
    predictor_path = os.path.join(settings.APPS_DIR, 'fixtures/plantilla_facial.dat')
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    print('Entrenando modelo...')
    # Se determinan los vectores caracteristicos de cada imagen
    [codificacion,nombres]=clasificador()

    print('Fin entrenamiento')
    while True:
        try:
           for cap in cameras:
               cap["src"].show_frame(cap["camera_id"])
        except AttributeError:
            pass