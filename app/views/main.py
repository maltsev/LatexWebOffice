# -*- coding: utf-8 -*-
"""

* Purpose :

* Creation Date : 22-10-2014

* Last Modified : Thu 07 Nov 2014 23:16:54 PM CET

* Author :  maltsev

* Coauthors :

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