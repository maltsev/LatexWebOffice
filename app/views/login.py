# -*- coding: utf-8 -*-
from django.shortcuts import render
from app.models.file import File


def index(request):
    return render(request, 'login.html', {'username': ''})