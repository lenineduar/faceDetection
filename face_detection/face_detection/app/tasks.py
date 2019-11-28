import cv2
import os
import numpy
import requests
import json
import base64

from django.conf import settings
from django.utils import timezone

from face_detection.app.models import Cameras, Notifications


def set_notifications(name, camara_id, image):
    camera = Cameras.objects.filter(pk=camara_id)
    name = name.replace("_", " ")
    notifications = Notifications.objects.filter(
        person_name=name, camera_description=camera[0].description).order_by("-created")
    current_time = timezone.now()
    if notifications:
        last_notification = notifications.first()
        time_elapsed = (current_time - last_notification.created).total_seconds()
        if time_elapsed > settings.MINIMUM_TIME_TO_NOTIFY:
            new_notification = Notifications(
                person_name = name,
                camera_description=camera[0].description,
                image_capture=image
            )
            new_notification.save()
    else:
        new_notification = Notifications(
            person_name = name,
            camera_description=camera[0].description,
            image_capture=image
        )
        new_notification.save()

    return None
