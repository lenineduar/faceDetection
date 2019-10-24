import cv2
from django.conf import settings
from django.shortcuts import render, redirect
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.views.generic import TemplateView, DetailView, View, ListView
from utils.camera import CameraStream, VideoStreaming
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse

from .models import Cameras

def set_cameras(pk):
    cameradb = Cameras.objects.filter(is_active=True, pk=pk)
    if cameradb:
        src = int(cameradb[0].src) if cameradb[0].src == '0' else cameradb[0].src
        cam = CameraStream(src).start()

        return cam
    else:
        return None


# Create your views here.
class IndexView(LoginRequiredMixin, View):
    redirect_unauthenticated_users = True 

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            return redirect('account_login')
        
        else:
            return redirect('dashboard')

        return super(IndexView, self).dispatch(*args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    redirect_unauthenticated_users = True
    template_name = "app/dashboard.html"

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            return redirect('account_login')

        return super(DashboardView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        cameras = []
        for i in range(1, settings.CAMERAS_ACTIVE+1):
            if Cameras.objects.filter(is_active=True, pk=i):
                camdb = Cameras.objects.filter(is_active=True, pk=i),
            else:
                camdb = None

            cam = {
                'camera': camdb, 
                'id': i,
                'slug': 'camera{}'.format(i),
                'url_stream': 'video{}_streaming'.format(i),
            }
            cameras.append(cam)

        context["cameras"] = cameras

        return context


class Video1StreamingView(LoginRequiredMixin, VideoStreaming, View):
    
    def __init__(self):
        self.camera = set_cameras(1)


class Video2StreamingView(LoginRequiredMixin, VideoStreaming, View):

    def __init__(self):
        self.camera = set_cameras(2)


class Video3StreamingView(LoginRequiredMixin, VideoStreaming, View):

    def __init__(self):
        self.camera = set_cameras(3)


class Video4StreamingView(LoginRequiredMixin, VideoStreaming, View):

    def __init__(self):
        self.camera = set_cameras(4)