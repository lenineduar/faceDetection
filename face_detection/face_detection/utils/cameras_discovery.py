from camera_discovery import CameraDiscovery
from face_detection.app.models import Cameras

def discovery():
	# Eliminar los objectos de la base de datos
    camerasdb = Cameras.objects.filter()
    for camera in camerasdb:
        camera.delete()

    i = 1
    cameras_discovery = CameraDiscovery.ws_discovery()
    for discovery in cameras_discovery:
        source = 'rtsp://admin:admin@'+discovery.replace(':','')+'/media/video1'
        cameradb = Cameras(
            pk = i, 
            is_active = True, 
            src = source,
            description = f"Camera {i}",
        )
        cameradb.save()
        i+=1