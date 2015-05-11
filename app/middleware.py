# -*- coding: utf-8 -*-
"""

* Purpose : Single Sign-on der WWU

* Creation Date : 11-05-2015

* Author :  maltsev

"""
from random import random

from django.contrib.auth import login
from django.contrib.auth.models import User


class SingleSignOnMiddleware:

    def process_request(self, request):
        if 'REMOTE_USER' not in request.META or request.user.is_authenticated():
            return

        user = self.get_user(request)
        if user:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)


    def get_user(self, request):
        remote_login = request.META.get('REMOTE_USER')
        if not remote_login:
            return None

        email = remote_login + '@uni-muenster.de'

        if User.objects.filter(email__iexact=email).exists():
            user = User.objects.get(email__iexact=email)
        else:
            full_name = request.META.get('HTTP_X_TRUSTED_REMOTE_NAME', '')
            user = self.register_user(email, full_name)

        return user


    def register_user(self, email, full_name):
        new_user = User.objects.create_user(email, email, password=str(random()))

        first_name, last_name = self.split_name(full_name)
        if first_name:
            new_user.first_name = first_name

        if last_name:
            new_user.last_name = last_name

        new_user.save()

        return new_user


    def split_name(self, full_name):
        name_parts = full_name.split('&nbsp;', 1)
        if len(name_parts) == 2:
            return name_parts
        else:
            return (name_parts[0], '')