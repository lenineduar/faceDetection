import cv2
import os
import dlib
import base64
import numpy as np
from django.conf import settings
from face_detection.app.tasks import set_notifications

def prediction(face_resize, camera_id, frame):
    dir_faces = os.path.join(settings.MEDIA_ROOT, 'att_faces/orl_faces')

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
    
    # Crear una matriz Numpy de las dos listas anteriores
    (images, lables) = [np.array(lis) for lis in [images, lables]]
    # OpenCV entrena un modelo a partir de las imagenes
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(images, lables)

    pred = model.predict(face_resize)

    cara = '%s' % (names[pred[0]])
    name = cara if pred[1]<100 else "Desconocido"

    if pred[1]<500:
        retval, buffer = cv2.imencode('.png', frame)
        png_as_text = base64.b64encode(buffer).decode('ascii')
        set_notifications(name, camera_id, png_as_text)

def prediction_fd(face_resize, camera_id, frame):
    # Crear una lista de imagenes y una lista de nombres correspondientes
    dir_faces = os.path.join(settings.MEDIA_ROOT, 'att_faces/orl_faces')
    (images, labels, names, id) = ([], [], {}, 0)
    print('Procesando base de datos...')
    for (subdirs, dirs, files) in os.walk(dir_faces):
        for subdir in dirs:
            names[id] = subdir
            subjectpath = os.path.join(dir_faces, subdir)
            for filename in os.listdir(subjectpath): 
                if filename!='Thumbs.db':
                    path = subjectpath + '/' + filename
                   
                    label = id
                    images.append(cv2.imread(path, 0))
                    labels.append(int(label))
                else:
                    continue
            id += 1
    print('Fin del procesamiento...')
    (im_width, im_height) = (112, 92)
    # Crear una matriz Numpy de las dos listas anteriores
    (images, labels) = [np.array(lis) for lis in [images, labels]]
    # OpenCV entrena un modelo a partir de las imagenes
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(images, labels)

    prediction = model.predict(face_resize)

    cara = '%s' % (names[prediction[0]])
    name = cara if prediction[1]<130 else "Desconocido"
    if prediction[1]<=500: #Rostro identificado
        retval, buffer = cv2.imencode('.png', frame)
        png_as_text = base64.b64encode(buffer).decode('ascii')
        set_notifications(name, camera_id, png_as_text)

    return names[prediction[0]], prediction

def landmarks_to_np(landmarks, dtype="int"):
    
        num = landmarks.num_parts
        
        # initialize the list of (x, y)-coordinates
        coords = np.zeros((num, 2), dtype=dtype)
        
        # loop over the 68 facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        for i in range(0, num):
            coords[i] = (landmarks.part(i).x, landmarks.part(i).y)
        # return the list of (x, y)-coordinates
        return coords

def get_centers(img, landmarks):
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
        
        pts = np.vstack((LEFT_EYE_CENTER,RIGHT_EYE_CENTER))
        cv2.polylines(img, [pts], False, (255,0,0), 1) #画回归线
        #cv2.circle(img, (LEFT_EYE_CENTER[0],LEFT_EYE_CENTER[1]), 3, (0, 0, 255), -1)
        #cv2.circle(img, (RIGHT_EYE_CENTER[0],RIGHT_EYE_CENTER[1]), 3, (0, 0, 255), -1)
        
        return LEFT_EYE_CENTER, RIGHT_EYE_CENTER

def get_aligned_face(img, left, right):
        desired_w = 256
        desired_h = 256
        desired_dist = desired_w * 0.5
        
        eyescenter = ((left[0]+right[0])*0.5 , (left[1]+right[1])*0.5)# 眉心
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

def judge_eyeglass(img):
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