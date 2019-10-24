from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.IndexView.as_view(), name="index"),
    path("dashboard", view=views.DashboardView.as_view(), name="dashboard"),
    


    path("video1/streaming", view=views.Video1StreamingView.as_view(), name="video1_streaming"),
    path("video2/streaming", view=views.Video2StreamingView.as_view(), name="video2_streaming"),
    path("video3/streaming", view=views.Video3StreamingView.as_view(), name="video3_streaming"),
    path("video4/streaming", view=views.Video4StreamingView.as_view(), name="video4_streaming"),
]
