from django.conf import settings
from django.utils import timezone

from face_detection.app.models import Cameras, Notifications

def set_notifications(name, camara_id):
    camera = Cameras.objects.filter(pk=camara_id)
    notifications = Notifications.objects.filter(person_name=name, camera=camera[0]).order_by("-created")
    current_time = timezone.now()
    if notifications:
        last_notification = notifications.first()
        time_elapsed = (current_time - last_notification.created).total_seconds()
        if time_elapsed > settings.MINIMUM_TIME_TO_NOTIFY:
            new_notification = Notifications(
                person_name = name,
                camera=camera[0]
            )
            new_notification.save()
    else:
        new_notification = Notifications(
            person_name = name,
            camera=camera[0]
        )
        new_notification.save()

    return None