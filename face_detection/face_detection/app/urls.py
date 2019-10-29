from django.urls import path

from . import views
from . import views_streaming as views_stream

urlpatterns = [
    path("", view=views.IndexView.as_view(), name="index"),
    path("dashboard", view=views.DashboardView.as_view(), name="dashboard"),
    path("notifications", view=views.ListNotificationsView.as_view(), name="list_notifications"),
    path("notification/<str:pk>", view=views.DetailNotificationView.as_view(), name="notification"),
    
    
    #URLs para las API servicios
    path("get/list/notifications", view=views.APIGetListNotifications.as_view(), name="get_list_notifications"),
    path("get/notification/<str:pk>/", view=views.APIGetNotification.as_view(), name="get_notification"),

    # URLs del servicio de Streaming
    path("video1/streaming", view=views_stream.Video1StreamingView, name="video1_streaming"),
    path("video2/streaming", view=views_stream.Video2StreamingView, name="video2_streaming"),
    path("video3/streaming", view=views_stream.Video3StreamingView, name="video3_streaming"),
    path("video4/streaming", view=views_stream.Video4StreamingView, name="video4_streaming"),


    path("frame/video/<str:camera>/", view=views_stream.FrameVideo, name="frame_video"),
]
