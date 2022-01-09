from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),

    # path('performance', views.PerformanceList.as_view()),
    # path('performance/create', views.PerformanceCreate.as_view()),
    # path('performance/<int:pk>', views.PerformanceRetrieveUpdateDestroy.as_view()),

    # path('order', views.OrderListCreate.as_view(), name="listcreateorder"),
    # path('order/<int:pk>', views.OrderRetrieveUpdateDestroy.as_view(),
    #      name='retrieveorder'),
]
