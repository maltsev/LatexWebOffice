# -*- coding: utf-8 -*-
"""

* Purpose :

* Creation Date : 22-10-2014

* Last Modified : Thu 07 Nov 2014 23:16:54 PM CET

* Author :  maltsev

* Coauthors : mattis

* Sprintnumber : 1

"""

from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from core.settings import LOGIN_URL

# see
# https://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.login

## Default handler for login requests by the client that sends the client the login page.
#  If correct login details were sent with the request (over POST data), the user will be redirected to a success page.
#  Otherwise an error message will be inserted into the django messages queue.
#  @param request The HttpRequest Object
def login(request):
    if request.user.is_authenticated():
        return redirect('/')

    email = ''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

         # Email is case-insensitive, but login is case-sensitive
        user = auth.authenticate(username=email.lower(), password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.error(request, '{0} ist aus ausgesperrt.'.format(email))

        else:
            messages.error(request, 'Email oder Passwort falsch.')


    return render(request, 'login.html', {'email': email})


## Registration page
#  @param request The HttpRequest Object
def registration(request):
    if request.user.is_authenticated():
        return redirect('/')

    return render(request, 'registration.html', {'username': '', 'email': ''})