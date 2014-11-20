# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url(r'^$', 'project.list'),
    url(r'^registration/', 'auth.registration'),
    url(r'^login/', 'auth.login'),
    url(r'^logout/', 'auth.logout'),
    url(r'^impressum/', 'main.impressum'),
    url(r'^hilfe/', 'main.hilfe'),
    url('^updatePdf','documents.exportToPdf'),
	url('^editor', 'main.editor'),
    url('^project/([0-9]+)/', 'project.editor')
)
