from django.apps import apps
from django.contrib import admin
from django.shortcuts import redirect

from .models import Vector, Operation


@admin.register(Vector)
class VectorAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/')

    def response_change(self, request, obj):
        return redirect('/')

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/')

    def response_change(self, request, obj):
        return redirect('/')


