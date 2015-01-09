# -*- coding: utf-8 -*-
"""

* Purpose : managing user account registration and login

* Creation Date : 22-10-2014

* Last Modified : Fr 09 Jan 2015 13:53:25 CET

* Author :  maltsev

* Coauthors : mattis, christian

* Sprintnumber : 1

* Backlog entry :  RUA1, RUA4

"""

from django.shortcuts import render,redirect, render_to_response
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.settings import LOGIN_URL
from app.common.constants import ERROR_MESSAGES
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.csrf import csrf_exempt
from django.template import Template, context, RequestContext
import re


# see
# https://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.login

## Default handler for login requests by the client that sends the client the login page.
#  If correct login details were sent with the request (over POST data), the user will be redirected to a success page.
#  Otherwise an error message will be inserted into the django messages queue.
#  @param request The HttpRequest Object
def login(request):
    if request.user.is_authenticated():
        return redirect('/projekt/')

    email = ''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

         # Email is case-insensitive, but login is case-sensitive
        user = auth.authenticate(username=email.lower(), password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('/projekt/')
            else:
                messages.error(request, ERROR_MESSAGES['INACTIVEACCOUNT'].format(email))

        else:
            messages.error(request, ERROR_MESSAGES['WRONGLOGINCREDENTIALS'])


    return render_to_response('login.html', {'email': email}, context_instance=RequestContext(request))


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
        return redirect('/projekt/')

    email = ''
    first_name = ''

    if request.method == 'POST':
        first_name = request.POST['first_name']
        email = request.POST['email'].lower()
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # boolean, true if there are errors in the user data
        foundErrors = False


        # validation checks
        # no empty fields
        if first_name == '' or email == '' or password1 == '':
            messages.error(request, ERROR_MESSAGES['NOEMPTYFIELDS'])
            foundErrors = True
        # email already registered
        if User.objects.filter(username=email).count() != 0:
            messages.error(request, ERROR_MESSAGES['EMAILALREADYEXISTS'])
            foundErrors = True
        # no valid email format
        if not validEmail(email):
            messages.error(request, ERROR_MESSAGES['INVALIDEMAIL'])
            foundErrors = True
        # passwords may not contain any spaces
        if ' ' in password1:
            messages.error((request), ERROR_MESSAGES['NOSPACESINPASSWORDS'])
            foundErrors = True
        # passwords do not match
        if password1 != password2:
            messages.error(request, ERROR_MESSAGES['PASSWORDSDONTMATCH'])
            foundErrors = True
        # if all validation checks pass, create new user
        if not foundErrors:
            new_user = User.objects.create_user(username=email, email=email,
                                                password=password1, first_name=first_name)

            # user login and redirection to start page
            user = auth.authenticate(username=email, password=password1)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return redirect('/projekt/')
            else:
                messages.error(request, ERROR_MESSAGES['LOGINORREGFAILED'])

    return render_to_response('registration.html', {'first_name': first_name, 'email': email}, context_instance=RequestContext(request))


@csrf_exempt
#Überprüft, ob eine Emailadresse bereits registiert ist. Falls sie registiert ist, wird false zurückgesendet. Andernfalls true.
def userexists(request):
    from django.http import HttpResponse
    if request.method=='POST' and request.POST.get('email'):
        if  User.objects.filter(username=request.POST.get('email')).exists():
            return HttpResponse("false")

    return HttpResponse('true')



# Helper function to check if a email address is valid
def validEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
