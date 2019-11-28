from django.contrib import admin
from .models import Cameras, Notifications, Person

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


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fullname',
        'is_white_list',
        'is_black_list',
        'created'
    )
    list_filter = ('id','fullname','is_white_list', 'is_black_list')
    search_fields = ['id','fullname','is_white_list', 'is_black_list']

admin.site.register(Person, PersonAdmin)

class NotificationsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'camera_description',
        'person_name',
        'is_ready',
        'created'
    )
    list_filter = ('id','camera_description','person_name','is_ready')
    search_fields = ['id','camera_description','person_name','is_ready']

admin.site.register(Notifications, NotificationsAdmin)