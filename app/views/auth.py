# -*- coding: utf-8 -*-
"""

* Purpose : managing user account registration and login

* Creation Date : 22-10-2014

* Last Modified : Thu 07 Nov 2014 23:16:54 PM CET

* Author :  maltsev

* Coauthors : mattis, christian

* Sprintnumber : 1

"""

from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.settings import LOGIN_URL
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
            messages.error(request, 'E-Mail-Adresse oder Passwort falsch.')


    return render(request, 'login.html')


## Logout
#  @param request The HttpRequest Object
@login_required
def logout(request):
    auth.logout(request)
    return redirect(LOGIN_URL)


## Default handler for registration requests by the client that sends the user the registration page.
#  If correct registration details were sent with the request (over POST data), the user will be logged in
#  and redirected to the start page
#  Otherwise an error message will be inserted into the django messages queue.
#  @param request The HttpRequest Object
def registration(request):

    if request.user.is_authenticated():
        return redirect('/')

    email = ''
    if request.method == 'POST':
        first_name = request.POST['first_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # validation checks
        # no empty fields
        if first_name == '' or email == '' or password1 == '':
            messages.error(request, 'Keine leeren Eingaben erlaubt.')
        # email already registered
        elif User.objects.filter(username=email).count() != 0:
            messages.error(request, 'E-Mail-Adresse ist bereits registriert.')
        # no valid email format
        elif not validEmail(email):
            messages.error(request, 'Ungültige E-Mail-Adresse.')
        # first name can not only contain spaces
        elif first_name.isspace():
            messages.error(request, 'Vorname darf nicht nur aus Leerzeichen bestehen.')
        # passwords do not match
        elif password1 != password2:
            messages.error(request, 'Passwörter stimmen nicht überein.')
        # if all validation checks pass, create new user
        else:
            new_user = User.objects.create_user(username=email.lower(), email=email.lower(),
                                                password=password1, first_name=first_name)

            # user login and redirection to start page
            user = auth.authenticate(username=email.lower(), password=password1)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return redirect('/')
            else:
                messages.error(request, 'Anmeldung nach Registrierung fehlgeschlagen.')

    return render(request, 'registration.html')


# Helper function to check if a email address is valid
def validEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False