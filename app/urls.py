# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.conf import settings
urlpatterns = patterns('app.views',
    url(r'^$', 'main.index'),
    url(r'^registration/', 'auth.registration'),
    url(r'^login/', 'auth.login'),
    url(r'^logout/', 'auth.logout'),
    url(r'^impressum/', 'main.impressum'),
    url(r'^hilfe/', 'main.hilfe'),
    url(r'^editor/', 'main.editor'),
    url(r'^documents/', 'document.execute'),
    url(r'^projekt/', 'main.projekt'),
    url(r'^dateien/', 'main.dateien'),
    url(r'^vorlagen/', 'main.vorlagen')
)
if settings.DEBUG:
    urlpatterns += patterns('app.views',
        (r'^documentPoster/', 'document.debug'),
    )
