# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.conf import settings


urlpatterns = patterns('app.views',
    url(r'^$', 'main.index', name='index'),
    url(r'^registration/', 'auth.registration', name='registration'),
    url(r'^reguserexists/', 'auth.userexists', name='reguserexists'),
    url(r'^login/', 'auth.login', name='login'),
    url(r'^logout/', 'auth.logout', name='logout'),
    url(r'^recoverpw/', 'auth.lostPwHandler',name='recoverpw'),
    url(r'^impressum/', 'main.impressum', name='impressum'),
    url(r'^editor/', 'main.editor', name='editor'),
    url(r'^documents/', 'document.execute', name='documents'),
    url(r'^projekt/', 'main.projekt', name='projekt'),
    url(r'^dateien/', 'main.dateien', name='dateien'),
    url(r'^vorlagen/', 'main.vorlagen', name='vorlagen'),
    url(r'^faq/', 'main.faq', name='faq'),
)
if settings.DEBUG:
    urlpatterns += patterns('app.views',
        (r'^documentPoster/', 'document.debug'),
    )
