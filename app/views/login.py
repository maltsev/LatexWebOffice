# -*- coding: utf-8 -*-
from django.shortcuts import render
from app.models.file import File
def index(request):
    username=''
    if request.method == 'POST':
        username = request.POST['username']

    return render(request, 'login.html', {'username': username})


def test(request):
    files = File.objects.all()[:2]
    return render(request, 'test.html', {'files': files})
