from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

# from .serializers import PerformanceSerializer
# from .serializers import OrderSerializer

from core.models import *

from rest_framework.pagination import PageNumberPagination

from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse

from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if data['password1'] != data['password2']:
            return JsonResponse({'error': 'Пароли не совпадают!'}, status=400)
        else:
            try:
                data = JSONParser().parse(request)
                user = User.objects.create_user(
                    data['username'], password=data['password1'], first_name=data['fio'], email=data['email'])
                new_group = Group.objects.get(name='allow_group')
                user.groups.add(new_group)
                user.save()
                token = Token.objects.create(user=user)
                return JsonResponse({'token': str(token)}, status=201)
            except IntegrityError:
                return JsonResponse({'error': 'Пользователь с данным логином уже существует!'}, status=400)
    else:
        return JsonResponse({'error': 'Разрешен только метод POST.'})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(
            request, username=data['username'], password=data['password'])
        if user is None:
            return JsonResponse({'error': 'Введен неверный логин или пароль!'}, status=400)
        else:
            new_group = Group.objects.get(name='allow_group')
            if user.groups.filter(name=new_group):
                return JsonResponse({'error': 'Ожидайте подтверждения администратором!'}, status=400)
            else:
                try:
                    token = Token.objects.get(user=user)
                except:
                    token = Token.objects.create(user=user)
                return JsonResponse({'token': str(token)}, status=200)
    else:
        return JsonResponse({'error': 'Разрешен только метод POST.'})
