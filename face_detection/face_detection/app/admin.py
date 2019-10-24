from django.contrib import admin
from .models import Cameras

class CamerasAdmin(admin.ModelAdmin):
    list_display = (
    	'id',
        'src',
        'is_active',
        'created'
    )
    list_filter = ('id','src','is_active')
    search_fields = ['id','src', 'is_active']

admin.site.register(Cameras, CamerasAdmin)