from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'password']


class TypeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeEvent
        fields = ['id', 'Name']


class TypeVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeVisitor
        fields = ['id', 'Name']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'startDate',
                  'endDate', 'address', 'type', 'description']


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id', 'event', 'arrivalDate', 'fullName', 'type']
