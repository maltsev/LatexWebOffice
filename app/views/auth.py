# -*- coding: utf-8 -*-
"""

* Purpose : managing user account registration and login

* Creation Date : 22-10-2014

* Last Modified : Sa 28 Feb 2015 00:19:42 CET

* Author :  maltsev

* Coauthors : mattis, christian

* Sprintnumber : 1

* Backlog entry :  RUA1, RUA4

"""

from django.shortcuts import render,redirect, render_to_response
from django.contrib import messages,auth
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from core.settings import LOGIN_URL
from app.common.constants import ERROR_MESSAGES
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.csrf import csrf_exempt
from django.template import Template, context, RequestContext
import re
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
import urllib
import datetime
from django.utils import timezone

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
    if request.session.has_key('email'):
        email=request.session.get('email')
        del request.session['email']
    if request.method == 'POST' and 'action' in request.POST and 'email' in request.POST:
        email = request.POST['email']
        if request.POST['action']=='login':
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
        elif request.POST['action']=='password-lost':
            if User.objects.filter(email__iexact=email).exists():
                user=User.objects.get(email__iexact=email)
                if (user.passwordlostdate+datetime.timedelta(minutes=5))<=timezone.now():
                    keygen = user.createrecoverkey()
                    user.save()
                    subject="Latexweboffice Passwortreset"
                    url=request.build_absolute_uri(reverse('recoverpw'))+'?'+urllib.parse.urlencode({'email':email,'key':keygen})
                    body="""
Hallo {0},

Jemand hat einen Link zur Passwortwiederherstellung angefordert: {1} 

Falls dies nicht von Ihnen angefordert wurde, ignorieren Sie bitte diese Email.

Mit freundlichen Grüßen,
Ihr LatexWebOfficeteam
                """
                    emailsend=EmailMessage(subject,body.format(email,url))
                    emailsend.to=[email]
                    emailsend.send()
            messages.success(request,ERROR_MESSAGES['EMAILPWRECOVERSEND'].format(email))
            


    return render_to_response('login.html', {'email': email}, context_instance=RequestContext(request))


def lostPwHandler(request):
    if request.method=='GET':
        if 'email' in request.GET and 'key' in request.GET:
            email=request.GET['email']
            key=request.GET['key']
            if User.objects.filter(email__iexact=email).exists():
                user=User.objects.get(email__iexact=email) 
                if user and user.passwordlostkey==key and ((user.passwordlostdate+datetime.timedelta(days=7))>=timezone.now()):
                    return render_to_response('passwordrecover.html',{'email':email,'key':key}, context_instance=RequestContext(request))

    elif request.method=='POST':
        if 'email' in request.POST and 'key' in request.POST and 'password1' in request.POST:
                    email=request.POST['email']
                    key=request.POST['key']
                    if User.objects.filter(email__iexact=email).exists():
                        user=User.objects.get(email__iexact=email) 
                        if user and user.passwordlostkey==key and ((user.passwordlostdate+datetime.timedelta(days=7))>=timezone.now()):
                            user.set_password(request.POST['password1'])
                            user.invalidateRecoverKey()
                            user.save()
                            messages.success(request,ERROR_MESSAGES['PASSWORDCHANGED'])
                            request.session['email']=email
                            return redirect('login')


    return render_to_response('passwordrecoverwrong.html',context_instance=RequestContext(request))

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
            new_user = User.objects.create_user(email=email,
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
    regex_email=re.compile("^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
    return regex_email.match(email)
