import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class Cameras(models.Model):
    src = models.CharField(max_length=255, blank=True, null=True, default='')
    description = models.CharField(max_length=255, blank=True, null=True, default='')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)


class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Cameras, on_delete=models.CASCADE,)
    person_name = models.CharField(max_length=255, blank=True, null=True, default='')
    is_ready = models.BooleanField(default=False)
    image_capture = models.TextField(default='', blank = True, null=True)
    created = models.DateTimeField(default=timezone.now)