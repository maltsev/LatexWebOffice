# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url(r'^$', 'main.index'),
    url(r'^registration/', 'registration.index'),
    url(r'^login/', 'login.index'),
)