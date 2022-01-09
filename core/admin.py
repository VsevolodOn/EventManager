from django.contrib import admin


from .models import *


class TypeEventAdmin(admin.ModelAdmin):
    list_display = ['name']


class TypeVisitorAdmin(admin.ModelAdmin):
    list_display = ['name']


class VisitorInLine(admin.StackedInline):
    model = Visitor


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'startDate', 'type']
    search_fields = ['name']
    inlines = [VisitorInLine]


class VisitorAdmin(admin.ModelAdmin):
    list_display = ['fullName']


admin.site.register(Event, EventAdmin)
admin.site.register(TypeEvent, TypeEventAdmin)
admin.site.register(TypeVisitor, TypeVisitorAdmin)
admin.site.register(Visitor, VisitorAdmin)
