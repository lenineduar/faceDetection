import cv2
import os
import base64
import numpy
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
    (images, lables) = [numpy.array(lis) for lis in [images, lables]]
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
    