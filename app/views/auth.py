# -*- coding: utf-8 -*-
"""

* Purpose : managing user account registration and login

* Creation Date : 22-10-2014

* Last Modified : Mo 10 Nov 2014 12:09:03 CET

* Author :  maltsev

* Coauthors : mattis, christian

* Sprintnumber : 1

"""

from django.shortcuts import render,redirect, render_to_response
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.settings import LOGIN_URL, ERROR_MESSAGES
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
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
        return redirect('/')

    email = ''
    first_name = ''

    if request.method == 'POST':
        first_name = request.POST['first_name']
        email = request.POST['email'].lower()
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # boolean, true if there are errors in the user data
        foundErrors = False

        # regular expression for first_name
        # should only contain ASCII characters 33 - 126 (hex: 21 - 7E)
        # and german special characters äöüß, no spaces allowed
        regex_first_name = re.compile('^[\x21-\x7EÄÖÜäöüß´°]*$')

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
        # first name may only contain standard ASCII characters
        # and some german special characters
        if not regex_first_name.match(first_name):
            messages.error(request, ERROR_MESSAGES['INVALIDCHARACTERINFIRSTNAME'])
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
                    return redirect('/')
            else:
                messages.error(request, ERROR_MESSAGES['LOGINORREGFAILED'])

    return render_to_response('registration.html', {'first_name': first_name, 'email': email}, context_instance=RequestContext(request))


# Helper function to check if a email address is valid
def validEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
