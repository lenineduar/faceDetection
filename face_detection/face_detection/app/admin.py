from django.contrib import admin
from .models import Cameras, Notifications

class CamerasAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'src',
        'description',
        'is_active',
        'created'
    )
    list_filter = ('id','src','is_active')
    search_fields = ['id','src','is_active']

admin.site.register(Cameras, CamerasAdmin)


class NotificationsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'camera',
        'person_name',
        'is_ready',
        'created'
    )
    list_filter = ('id','camera','person_name','is_ready')
    search_fields = ['id','camera','person_name','is_ready']

admin.site.register(Notifications, NotificationsAdmin)