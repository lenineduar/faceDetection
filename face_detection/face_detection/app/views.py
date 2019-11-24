
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
        
        context["notifications"] = notifications
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

        if not person_name.lower().capitalize() == "Desconocido":
            person = Person.objects.filter(fullname=person_name)
            if not person:
                person = Person(fullname=person_name)
                person.save()
        
        notification.person_name = person_name
        notification.save()

        return redirect("notification", pk=notification.id)


class ListPersonsView(LoginRequiredMixin, ListView):
    redirect_unauthenticated_users = True
    template_name = "app/list_persons.html"
    model = Person
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ListPersonsView, self).get_context_data(**kwargs)
        persons = Person.objects.all().order_by('-created')
        context["persons"] = persons
        context["nav_persons"] = "active"

        return context


class EditPersonView(LoginRequiredMixin, View):
    redirect_unauthenticated_users = True

    def post(self, request, *args, **kwargs):
        person = get_object_or_404(Person, pk=kwargs['pk'])
        person_name = request.POST.get("person_name", None)
        is_white_list = request.POST.get("whitelist", False)
        is_black_list = request.POST.get("blacklist", False)

        if person_name:
            person.fullname = person_name
            person.is_white_list = True if is_white_list == "on" else False
            person.is_black_list = True if is_black_list == "on" else False
            person.save()

        return redirect("list_persons")



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


class APIGetPerson(LoginRequiredMixin, View):
    def dispatch(self, *args, **kwargs):
        return super(APIGetPerson, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        person = get_object_or_404(Person, pk=kwargs['pk'])
        p = {
            'id': person.id,
            'fullname': person.fullname,
            'is_white_list': person.is_white_list,
            'is_black_list': person.is_black_list,
            'created': change_utc_date(person.created),
        }

        return JsonResponse(p, safe=False)