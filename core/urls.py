from django.contrib import admin
from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login', views.login_view, name="login"),
    path('signup', views.signup_view, name="signup"),
    path('logout', auth_views.LogoutView.as_view(
        next_page="login"), name="logout"),
    path('personal', views.personal_view, name="personal"),

    path('', views.events_view, name="events"),
    path('event-<int:id>', views.event_view, name="event"),
    path('event-delete-<int:id>', views.event_delete, name="event_delete"),
    path('visitor-delete-<int:id>', views.visitor_delete, name="visitor_delete"),

]
