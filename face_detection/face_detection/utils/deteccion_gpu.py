import face_recognition
import pickle
import os
from django.conf import settings

# Se entrena un clasificador SVM

# Se determina el vector de caracteristicas faciales y losnombres correspondientes
def clasificador():
    encodings = []
    names = []

    # Directorio con imagenes de entrenamiento
    directorio = os.path.join(settings.MEDIA_ROOT, 'att_faces/orl_faces/')
    train_dir = os.listdir(directorio)

    # Se recorre cada persona en la base de datos
    for person in train_dir:
        pix = os.listdir(directorio + person)

        # Se recorre cada imagen de la persona
        for person_img in pix:
            #Se Obtienen las codificaciones de cara para la cara en cada archivo de imagen
            face = face_recognition.load_image_file(directorio + person + "/" + person_img)
            face_bounding_boxes = face_recognition.face_locations(face)

            #Si la imagen de entrenamiento contiene una sola cara
            if len(face_bounding_boxes) == 1:
                face_enc = face_recognition.face_encodings(face)[0]
                #Se agrega la codificación facial para la imagen actual con la etiqueta correspondiente (nombre) a los datos de entrenamiento
                encodings.append(face_enc)
                names.append(person)
            else:
                print(person + "/" + person_img + " no puede usarse para entrenar")

    return encodings, names
    