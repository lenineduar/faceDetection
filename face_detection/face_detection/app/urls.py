from django.urls import path

from . import views, views_streaming

urlpatterns = [
    path("", view=views.IndexView.as_view(), name="index"),
    path("dashboard", view=views.DashboardView.as_view(), name="dashboard"),
    path("notifications", view=views.ListNotificationsView.as_view(), name="list_notifications"),
    path("capture/face/name", view=views.CaptureFaceNameView.as_view(), name="capture_face_name"),
    path("notification/<str:pk>", view=views.DetailNotificationView.as_view(), name="notification"),
    path("notification/edit/<str:pk>", view=views.EditNotificationView.as_view(), name="edit_notification"),
    path("notification/delete/<str:pk>", view=views.DeleteNotificationsView.as_view(), name="del_notification"),
    
    path("persons", view=views.ListPersonsView.as_view(), name="list_persons"),
    path("person/edit/<str:pk>", view=views.EditPersonView.as_view(), name="edit_person"),
    
    path("add/image/edit/<str:pk>", view=views.AddImageToRecognitionView.as_view(), name="add_img_edit"),

    #URLs para las API servicios
    path("get/cameras/actives", view=views.APIGetCamerasActives.as_view(), name="get_cameras_actives"),
    path("get/list/notifications", view=views.APIGetListNotifications.as_view(), name="get_list_notifications"),
    path("get/notification/<str:pk>/", view=views.APIGetNotification.as_view(), name="get_notification"),
    path("get/person/<str:pk>/", view=views.APIGetPerson.as_view(), name="get_person"),

    path("run/capture/face", view=views.APIRunCaptureFace.as_view(), name="run_capture_face"),

    # URLs del servicio de Streaming
    path("video/streaming", view=views_streaming.VideoStreamingCaptureView, name="video_streaming_capture"),
    # path("video2/streaming", view=views_stream.Video2StreamingView, name="video2_streaming"),
    # path("video3/streaming", view=views_stream.Video3StreamingView, name="video3_streaming"),
    # path("video4/streaming", view=views_stream.Video4StreamingView, name="video4_streaming"),


    # path("frame/video/<str:camera>/", view=views_stream.FrameVideo, name="frame_video"),
]
