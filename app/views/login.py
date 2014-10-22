# -*- coding: utf-8 -*-
from django.shortcuts import render
from app.models.file import File

def index(request):
    return render(request, 'login.html', {'text': 'Hallo!'})


def test(request):
    files = File.objects.all()[:5]
    return render(request, 'test.html', {'files': files})