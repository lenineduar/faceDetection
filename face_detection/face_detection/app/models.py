from django.db import models
from django.utils import timezone

# Create your models here.
class Cameras(models.Model):
    src = models.CharField(max_length=255, blank=True, null=True, default='')
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)