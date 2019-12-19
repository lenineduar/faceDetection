import requests
import json
from django.conf import settings
from pytz import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import uuid

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


class EMail(object):
    def __init__(self, to, subject, cc=[], bcc=[]):
        self.to = to
        self.subject = subject
        self.cc = cc
        self.bcc = bcc
        self._html = None
        self._text = None
        self._random_string = str(uuid.uuid4())

    def _render(self, template, context):
        return render_to_string(template, context)

    def html(self, template, context):
        self._html = self._render(template, context)

    def text(self, template, context):
        self._text = self._render(template, context)

    def send(self, from_addr=None, fail_silently=False):
        if isinstance(self.to, str):
            self.to = [self.to]
        if not from_addr:
            from_addr = settings.EMAIL_FROM_ADDR
            # generate random address
            address_string = from_addr.split('@')
            from_addr = 'MFA <{0}-{1}@{2}>'.format(
                address_string[0],
                self._random_string,
                address_string[1]
            )

        msg = EmailMultiAlternatives(
            self.subject,
            self._text,
            from_addr,
            self.to,
            bcc=self.bcc,
            cc=self.cc
        )

        if self._html:
            msg.attach_alternative(self._html, 'text/html')

        msg.send(fail_silently)