from django.db.models.fields import TimeField
from django.shortcuts import render
from django.core.paginator import Paginator

from core import analyzer
from .models import *

from .forms import *
from django.urls import reverse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, logout, login

from django.views.decorators.csrf import requires_csrf_token

from django.middleware import csrf

from rest_framework.parsers import JSONParser
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from django.core.mail import send_mail
from django.conf import settings
from .analyzer import AnalysisEvent


def events_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if 'term' in request.GET:
        qsname = request.GET.get('term')
        qsname = qsname.strip()
        qs = Event.objects.filter(name__icontains=qsname)
        names = list()
        for event in qs:
            names.append(event.name)
        return JsonResponse(names, safe=False)

    qsname = ""
    if 'qsname' in request.GET:
        qsname = request.GET.get('qsname')

    page_number = request.GET.get('page')
    if request.method == "POST":
        if 'events' in request.POST:
            qsname = request.POST.get('events')
            qsname = qsname.strip()
            if len(qsname) != 0:
                events = Event.objects.filter(name__icontains=qsname)
                page_number = 1
            else:
                events = Event.objects.all()
        else:
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                event = Event()
                event.name = event_form.cleaned_data['name']
                event.startDate = event_form.cleaned_data['startDate']
                event.endDate = event_form.cleaned_data['endDate']
                event.address = event_form.cleaned_data["address"]
                event.type = event_form.cleaned_data["type"]
                event.description = event_form.cleaned_data["description"]
                event.save()
                return HttpResponseRedirect(reverse("event", args=(event.id,)))
            else:
                return HttpResponseRedirect(reverse("events"))
    else:
        events = Event.objects.all()

    paginator = Paginator(events, 5)
    page_obj = paginator.get_page(page_number)
    minp = page_obj.paginator.page_range[0]
    maxp = page_obj.paginator.page_range[-1]
    if page_obj.number - minp > 2:
        minp = page_obj.number-2
    if maxp-page_obj.number > 2:
        maxp = page_obj.number+2

    form = EventForm()
    template = "core/events.html"
    context = {
        'events': page_obj,
        'qsname': qsname,
        'minp': minp,
        'maxp': maxp,
        'mina': page_obj.paginator.page_range[0],
        'maxa': page_obj.paginator.page_range[-1],
        'form': form,
    }
    return render(request, template, context)


def event_view(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    page = ''
    qsname = ''
    if 'page' in request.GET:
        page = request.GET.get('page')
    if 'qsname' in request.GET:
        qsname = request.GET.get('qsname')

    urargs = ''
    if page or qsname:
        if page:
            urargs = urargs+'page='+page
        if qsname:
            urargs = urargs+'&qsname='+qsname

    if request.method == "POST":
        # Изменение данных
        if request.POST.get("startDate"):
            event = Event.objects.get(id=id)
            event.name = request.POST.get("name")
            event.startDate = request.POST.get("startDate")
            event.endDate = request.POST.get("endDate")
            event.address = request.POST.get("address")
            event.type = TypeEvent.objects.get(id=request.POST.get("type"))
            event.description = request.POST.get("description")
            event.save()
            if urargs:
                return HttpResponseRedirect(reverse("event", args=[id])+'?'+urargs)
            return HttpResponseRedirect(reverse("event", args=[id]))
        elif request.POST.get("arrivalDate"):
            visitor_form = VisitorForm(request.POST)
            if visitor_form.is_valid():
                visitor = Visitor()
                visitor.event = Event.objects.get(id=id)
                visitor.arrivalDate = visitor_form.cleaned_data['arrivalDate']
                visitor.fullName = visitor_form.cleaned_data['fullName']
                visitor.type = visitor_form.cleaned_data['type']
                visitor.save()
        if urargs:
            return HttpResponseRedirect(reverse("event", args=[id])+'?'+urargs+"#list-visitors")
        return HttpResponseRedirect(reverse("event", args=[id])+"#list-visitors")

    template = "core/event.html"
    event = Event.objects.get(id=id)

    eform = EventForm()
    eform.fields["name"].initial = event.name
    eform.fields["startDate"].initial = event.startDate
    eform.fields["endDate"].initial = event.endDate
    eform.fields["address"].initial = event.address
    eform.fields["type"].initial = event.type
    eform.fields["description"].initial = event.description
    vform = VisitorForm()

    visitors = Visitor.objects.filter(event=event)
    page_number = request.GET.get('vpage')
    paginator = Paginator(visitors, 5)
    page_obj = paginator.get_page(page_number)
    minp = page_obj.paginator.page_range[0]
    maxp = page_obj.paginator.page_range[-1]
    if page_obj.number - minp > 2:
        minp = page_obj.number-2
    if maxp-page_obj.number > 2:
        maxp = page_obj.number+2

    analys = AnalysisEvent(event.id)
    context = {
        'event': event,
        'eform': eform,
        'vform': vform,
        'urargs': urargs,
        'visitors': page_obj,
        'minp': minp,
        'maxp': maxp,
        'mina': page_obj.paginator.page_range[0],
        'maxa': page_obj.paginator.page_range[-1],
        'acount': analys.get_num_visitors(),
        'vcounts': analys.get_num_visitors_by_type(),
        'meandata': analys.get_mean_time(),
        'maxdata': analys.get_max_time(),
        'mindata': analys.get_min_time(),
        'mediandata': analys.get_median_time(),
        'q1data': analys.get_q1_time(),
        'q3data': analys.get_q3_time()
    }

    return render(request, template, context)


def event_delete(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if Event.objects.all().filter(id=id):
        Event.objects.all().filter(id=id).delete()

    return HttpResponseRedirect(reverse("events"))


def visitor_delete(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    page = ''
    qsname = ''
    if 'page' in request.GET:
        page = request.GET.get('page')
    if 'qsname' in request.GET:
        qsname = request.GET.get('qsname')
    urargs = ''
    if page or qsname:
        if page:
            urargs = urargs+'page='+page
        if qsname:
            urargs = urargs+'&qsname='+qsname

    if Visitor.objects.all().filter(id=id):
        vis = Visitor.objects.all().get(id=id)
        ide = vis.event.id
        vis.delete()

    return HttpResponseRedirect(reverse("event", args=[ide])+('?'+urargs if urargs else "")+"#list-visitors")

# Вход


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("events"))

    if request.method == "POST":
        auth_form = AuthForm(request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(
                request, username=username, password=password)
            if user is None:
                auth_form.add_error(
                    '__all__', 'Введен неверный логин или пароль!')
            else:
                new_group = Group.objects.get(name='allow_group')
                if user.groups.filter(name=new_group):
                    auth_form.add_error(
                        '__all__', 'Ожидайте подтверждения администратором!')
                else:
                    login(request, user)
                    return HttpResponseRedirect(reverse("events"))
        else:
            auth_form.add_error('__all__', 'Ошибка ввода.')
        template = "core/login.html"
        context = {
            'form': auth_form
        }
        return render(request, template, context)
    else:
        template = "core/login.html"
        auth_form = AuthForm()
        context = {
            'form': auth_form
        }
        if 'mes' in request.GET:
            context['mes'] = 'Данные отправлены. Ожидайте подтверждения администратором.'
        return render(request, template, context)

# Регистрация


def signup_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("events"))

    if request.method == "POST":
        auth_form = SignForm(request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password1 = auth_form.cleaned_data['password1']
            password2 = auth_form.cleaned_data['password2']
            name = auth_form.cleaned_data['name']
            email = auth_form.cleaned_data['email']
            if password1 == password2:
                if User.objects.all().filter(username=username):
                    auth_form.add_error(
                        '__all__', 'Пользователь с данным именем уже существует!')
                else:
                    user = User.objects.create_user(
                        username=username, password=password1, first_name=name, email=email)
                    new_group = Group.objects.get(name='allow_group')
                    user.groups.add(new_group)
                    user.save()

                    send_mail(subject='New user',
                              message='User: ' + username+';\nEmail: '+email+';\nName: '+name+';',
                              from_email=settings.EMAIL_HOST_USER,
                              recipient_list=[settings.RECIPIENT_ADDRESS])
                    return redirect('%s?mes=1' % reverse('login'))

            else:
                auth_form.add_error(
                    '__all__', 'Пароли не совпадают!')
        else:
            auth_form.add_error('__all__', 'Ошибка ввода.')
        template = "core/signup.html"
        context = {
            'form': auth_form
        }
        return render(request, template, context)
    else:
        template = "core/signup.html"
        auth_form = SignForm()
        context = {
            'form': auth_form
        }
        return render(request, template, context)

# Личный кабинет


def personal_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    template = "core/personal_cabinet.html"

    context = {
        'user': request.user
    }
    return render(request, template, context)


def help_view(request):
    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    event = Event()
    event.name = "Мероприятие 1"
    event.address = "Адрес 1"
    event.type = TypeEvent.objects.all()[0]
    event.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    event.save()

    return redirect(reverse('events'))
