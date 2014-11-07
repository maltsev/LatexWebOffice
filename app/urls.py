# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url(r'^$', 'main.index'),
    url(r'^registration/', 'auth.registration'),
    url(r'^login/', 'auth.login')
)