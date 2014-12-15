# -*- coding: utf-8 -*-
"""

* Purpose :

* Creation Date : 22-10-2014

* Last Modified : Su 14 Dec 2014 08:56:18 PM CET

* Author :  maltsev

* Coauthors : ingo

* Sprintnumber : 1

"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'index.html')

def impressum(request):
    return render(request, 'impressum.html')

def hilfe(request):
    return render(request, 'hilfe.html')

@login_required
def editor(request):
    return render(request, 'editor.html')

@login_required
def projekt(request):
    return render(request, 'projekt.html')

@login_required
def vorlagen(request):
    return render(request, 'vorlagen.html')
