import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class Cameras(models.Model):
    src = models.CharField(max_length=255, blank=True, null=True, default='')
    description = models.CharField(max_length=255, blank=True, null=True, default='')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=255, blank=True, null=True, default='')
    is_white_list = models.BooleanField(default=False)
    is_black_list = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)


class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera_description = models.CharField(max_length=255, blank=True, null=True, default='')
    person_name = models.CharField(max_length=255, blank=True, null=True, default='')
    is_ready = models.BooleanField(default=False)
    image_capture = models.TextField(default='', blank = True, null=True)
    created = models.DateTimeField(default=timezone.now)

    def get_person(self):
        person = Person.objects.filter(fullname=self.person_name)
        return {
            'is_person': True if person else False,
            'is_white_list': person[0].is_white_list if person else None,
            'is_black_list': person[0].is_black_list if person else None,
        }
