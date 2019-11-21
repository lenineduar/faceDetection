
import sys
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from braces.views import LoginRequiredMixin, GroupRequiredMixin
from django.views.generic import TemplateView, DetailView, View, ListView
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from .utils import change_utc_date
#from utils.cameras_discovery import discovery

from .models import Cameras, Notifications, Person


#if sys.argv[1] == "runserver":
#    discovery()


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
                camdb = Cameras.objects.filter(is_active=True, pk=i).first(),
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
        context["nav_dashboard"] = "active"
        context["cam_test"] = Cameras.objects.filter(is_active=True, pk=1).first()

        return context


class ListNotificationsView(LoginRequiredMixin, ListView):
    redirect_unauthenticated_users = True
    template_name = "app/list_notifications.html"
    model = Notifications
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ListNotificationsView, self).get_context_data(**kwargs)
        notifications = Notifications.objects.all().order_by('-created')

        paginator = Paginator(notifications, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            paginated_list = paginator.page(page)
        except PageNotAnInteger:
            paginated_list = paginator.page(1)
        except EmptyPage:
            paginated_list = paginator.page(paginator.num_pages)

        context["notifications"] = paginated_list
        context["nav_notifications"] = "active"

        return context


class DetailNotificationView(LoginRequiredMixin, DetailView):
    redirect_unauthenticated_users = True
    template_name = "app/notification.html"
    model = Notifications

    def get_context_data(self, **kwargs):
        context = super(DetailNotificationView, self).get_context_data(**kwargs)
        self.object.is_ready = True
        self.object.save()
        context["notification"] = self.object

        return context


class EditNotificationView(LoginRequiredMixin, DetailView):
    redirect_unauthenticated_users = True
    template_name = "app/edit_notification.html"
    model = Notifications

    def get_context_data(self, **kwargs):
        context = super(EditNotificationView, self).get_context_data(**kwargs)
        self.object.is_ready = True
        self.object.save()
        context["notification"] = self.object
        context["persons"] = Person.objects.filter()

        return context

    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(Notifications, pk=kwargs['pk'])
        person_name = request.POST.get("person_name","Desconocido")
        whitelist = request.POST.get("whitelist", "")
        blacklist = request.POST.get("blacklist", "")

        if not person_name.lower().capitalize() == "Desconocido":
            notification.person_name = person_name
            person = Person.objects.filter(fullname=person_name)
            w_list = True if whitelist == "on" else False
            b_list = True if blacklist == "on" else False
            if person:
                person = person[0]
            else:
                person = Person(fullname=person_name)

            person.is_white_list = w_list
            person.is_black_list = b_list
            person.save()
            notification.save()

        return redirect("notification", pk=notification.id)


# -------------------------------------------------------
# Api Section
# -------------------------------------------------------
class APIGetCamerasActives(View):
    def dispatch(self, *args, **kwargs):
        return super(APIGetCamerasActives, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        cameras = []
        camerasdb = Cameras.objects.filter(is_active=True)
        for camdb in camerasdb:
            cam = {
               'id': camdb.id,
               'src': camdb.src
            }
            cameras.append(cam)

        return JsonResponse(cameras, safe=False)


class APIGetListNotifications(LoginRequiredMixin, View):
    def dispatch(self, *args, **kwargs):
        return super(APIGetListNotifications, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        notifications = Notifications.objects.all()
        not_read_not = notifications.filter(is_ready=False).count()
        notifications = notifications.order_by("-created")[:5]
        info = []
        for notification in notifications:
            notif = {
                'id': notification.id,
                'person_name': notification.person_name.upper(),
                'is_ready': notification.is_ready,
                'created': change_utc_date(notification.created),
                'cam_description': notification.camera.description
            }
            info.append(notif)

        data = {
            'notifications': info,
            'not_read_not': not_read_not,
        }
        return JsonResponse(data, safe=False)


class APIGetNotification(LoginRequiredMixin, View):
    def dispatch(self, *args, **kwargs):
        return super(APIGetNotification, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        notification = get_object_or_404(Notifications, pk=kwargs['pk'])
        notif = {
            'id': notification.id,
            'person_name': notification.person_name,
            'is_ready': notification.is_ready,
            'created': change_utc_date(notification.created),
            'cam_description': notification.camera.description,
            'image': 'data:image/png;base64,%s' % (notification.image_capture) if notification.image_capture else ''
        }
        notification.is_ready = True
        notification.save()

        return JsonResponse(notif, safe=False)