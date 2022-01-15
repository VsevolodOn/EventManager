from django.db import models

from datetime import datetime

from django.conf import settings


class TypeEvent(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')

    def __str__(self):
        return self.name


class TypeVisitor(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name='name')
    startDate = models.DateTimeField(default=datetime.now)
    endDate = models.DateTimeField(default=datetime.now)
    address = models.CharField(max_length=200, verbose_name='address')
    type = models.ForeignKey(
        TypeEvent, on_delete=models.PROTECT, verbose_name='type')
    description = models.TextField(
        max_length=5000, verbose_name='description', default="", blank=True)

    class Meta():
        verbose_name = 'Event'
        verbose_name_plural = 'Event'
        ordering = ('-startDate',)


class Visitor(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, verbose_name='performance')
    arrivalDate = models.DateTimeField(default=datetime.now)
    fullName = models.CharField(max_length=200, verbose_name='fullName')
    type = models.ForeignKey(
        TypeVisitor, on_delete=models.PROTECT, verbose_name='type')

    class Meta:
        verbose_name_plural = 'Visitor'
        verbose_name = 'Visitor'
        ordering = ('-arrivalDate',)
