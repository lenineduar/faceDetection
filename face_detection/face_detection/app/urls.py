from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.IndexView.as_view(), name="index"),
    path("dashboard", view=views.DashboardView.as_view(), name="dashboard"),
    path("notifications", view=views.ListNotificationsView.as_view(), name="list_notifications"),
    
    
    #URLs para las API servicios
    path("get/list/notifications", view=views.APIGetListNotifications.as_view(), name="get_list_notifications"),
    path("get/notification/<str:pk>/", view=views.APIGetNotification.as_view(), name="get_notification"),

    # URLs de el servicio de Streaming
    path("video1/streaming", view=views.Video1StreamingView.as_view(), name="video1_streaming"),
    path("video2/streaming", view=views.Video2StreamingView.as_view(), name="video2_streaming"),
    path("video3/streaming", view=views.Video3StreamingView.as_view(), name="video3_streaming"),
    path("video4/streaming", view=views.Video4StreamingView.as_view(), name="video4_streaming"),
]
