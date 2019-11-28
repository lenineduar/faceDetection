import requests
import json
from django.conf import settings
from pytz import timezone

from face_detection.app.models import Cameras

def change_utc_date(date):
    date_utc = date.astimezone(timezone(settings.TIME_ZONE))
    return date_utc.strftime("%d-%m-%Y @ %H:%M:%S")

def replace_special_character(name):
    name = name.replace("á", "a"
    	).replace("é", "e"
    	).replace("í", "i"
    	).replace("ó", "o"
    	).replace("ú","u"
    	).replace("ñ", "n")
    
    return name

def discovery():
	# Eliminar los objectos de la base de datos
    camerasdb = Cameras.objects.filter()
    for camera in camerasdb:
        camera.delete()

    i = 1
    response = requests.get("http://localhost:5000/cameras")
    cameras_discovery = response.json()["uri"]
    for source in cameras_discovery:
        cameradb = Cameras(
            pk = i, 
            is_active = True, 
            src = source,
            description = f"Camera {i}",
        )
        cameradb.save()
        i+=1