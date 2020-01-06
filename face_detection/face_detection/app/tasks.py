import cv2
import os
import numpy
import requests
import json
import base64

from django.conf import settings
from django.utils import timezone

from face_detection.app.utils import EMail
from face_detection.app.models import Cameras, Notifications
from threading import Thread


def set_notifications(name, camara_id, image):
    camera = Cameras.objects.filter(pk=camara_id)
    name = name.replace("_", " ")
    notifications = Notifications.objects.filter(
        person_name=name, camera_description=camera[0].description).order_by("-created")
    current_time = timezone.now()
    if name == "Desconocido":
        minimum_time = settings.MINIMUM_TIME_TO_NOTIFY_UNKNOW
    else:
        minimum_time = settings.MINIMUM_TIME_TO_NOTIFY
    if notifications:
        last_notification = notifications.first()
        time_elapsed = (current_time - last_notification.created).total_seconds()
        if time_elapsed > minimum_time:
            new_notification = Notifications(
                person_name = name,
                camera_description=camera[0].description,
                image_capture=image
            )
            new_notification.save()
            send = Thread(target=send_mail_notification, args=(new_notification,))
            send.start()
            #send_mail_notification(new_notification)
    else:
        new_notification = Notifications(
            person_name = name,
            camera_description=camera[0].description,
            image_capture=image
        )
        new_notification.save()
        send = Thread(target=send_mail_notification, args=(new_notification,))
        send.start()
        #send_mail_notification(new_notification)

    return None

def send_mail_notification(notification):
    try:
        ctx = {
            'notification': notification,
            'admin': settings.EMAIL_NOTIFY_DETECTION,
        }

        # Send the Email
        email = EMail(
            to=settings.EMAIL_NOTIFY_DETECTION,
            subject=f"Nueva Detección - Persona: {notification.person_name}",
        )

        email.text('app/emails/nueva_deteccion.txt', ctx)
        email.html('app/emails/nueva_deteccion.html', ctx)
        email.send()
        print("Se envió")
    except Exception as e:
        print("No se envió")
        pass

    return None