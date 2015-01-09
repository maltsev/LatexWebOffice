# -*- coding: utf-8 -*-
"""

* Purpose :

* Creation Date : 22-10-2014

* Last Modified : Mi 07 Jan 2015 16:43:33 CET

* Author :  maltsev

* Coauthors : ingo

* Sprintnumber : 1

"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')

def impressum(request):
    return render(request, 'impressum.html')

def hilfe(request):
    return render(request, 'hilfe.html')
	
def faq(request):
    return render(request, 'faq.html')

@login_required
def editor(request):
    return render(request, 'editor.html')

@login_required
def projekt(request):
    return render(request, 'projekt.html')

@login_required
def vorlagen(request):
    return render(request, 'vorlagen.html')

@login_required
def dateien(request):
    return render(request,'dateien.html')
