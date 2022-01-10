from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError


from .serializers import *

from core.models import *

from rest_framework.pagination import PageNumberPagination

from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse

from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout

from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from core.analyzer import AnalysisEvent


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            if data['password1'] != data['password2']:
                return JsonResponse({'error': 'Пароли не совпадают!'}, status=400)
            else:
                user = User.objects.create_user(
                    data['login'], password=data['password1'], first_name=data['fio'], email=data['email'])
                new_group = Group.objects.get(name='allow_group')
                user.groups.add(new_group)
                user.save()
                token = Token.objects.create(user=user)
                return JsonResponse({'info': 'Регистрация выполнена успешно. Ожидайте подтверждение администратором.'}, status=201)
        except IntegrityError:
            return JsonResponse({'error': 'Пользователь с данным логином уже существует!'}, status=400)
        except:
            return JsonResponse({'error': 'Ошибка формата данных!'}, status=400)
    else:
        return JsonResponse({'error': 'Разрешен только метод POST.'})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = authenticate(
                request, username=data['login'], password=data['password'])
            if user is None:
                return JsonResponse({'error': 'Введен неверный логин или пароль!'}, status=400)
            else:
                new_group = Group.objects.get(name='allow_group')
                if user.groups.filter(name=new_group):
                    return JsonResponse({'info': 'Ожидайте подтверждения администратором!'}, status=400)
                else:
                    try:
                        token = Token.objects.get(user=user)
                    except:
                        token = Token.objects.create(user=user)
                    return JsonResponse({'token': str(token)}, status=200)
        except:
            return JsonResponse({'error': 'Ошибка формата данных!'}, status=400)
    else:
        return JsonResponse({'error': 'Разрешен только метод POST.'})


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['pk'])


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        return Response({"id": user.id, "login": user.username, "fio": user.first_name, "email": user.password})

    def delete(self, request):
        self.request.user.auth_token.delete()
        logout(request)
        return Response({"make": "Ok!"})


class AnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Event.objects.all(), pk=pk)
        analys = AnalysisEvent(pk)
        return Response({"acount": analys.get_num_visitors(),
                         "vcounts": analys.get_num_visitors_by_type(),
                         "meandata": analys.get_mean_time(),
                         "maxdata": analys.get_max_time(),
                         "mindata": analys.get_min_time(),
                         "mediandata": analys.get_median_time(),
                         "q1data": analys.get_q1_time(),
                         "q3data": analys.get_q3_time()})


class EventListCreate(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.all()


class EventRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(id=self.kwargs['pk'])


class VisitorListCreate(generics.ListCreateAPIView):
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Visitor.objects.filter(event_id=self.kwargs['pk'])


class VisitorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Visitor.objects.filter(id=self.kwargs['pk'])
