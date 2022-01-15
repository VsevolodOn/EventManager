from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),
    path('user', views.UserView.as_view()),
    path('user-update/<int:pk>', views.UserUpdateView.as_view()),
    path('analysis', views.AnalyzesView.as_view()),
    path('analysis/<int:pk>', views.AnalysisView.as_view()),


    path('event', views.EventListCreate.as_view()),
    path('event/<int:pk>', views.EventRetrieveUpdateDestroy.as_view()),
    path('event/<int:pk>/visitor', views.VisitorListCreate.as_view()),
    path('visitor/<int:pk>', views.VisitorRetrieveUpdateDestroy.as_view()),
]
