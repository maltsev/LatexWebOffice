# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.base import RedirectView

urlpatterns = patterns('app.views',
    url(r'^$', 'main.index'),
    url(r'^registration/', 'auth.registration'),
    url(r'^reguserexists/', 'auth.userexists'),
    url(r'^login/', 'auth.login', name='login'),
    url(r'^logout/', 'auth.logout'),
    url(r'^recoverpw/', 'auth.lostPwHandler',name='recoverpw'),
    url(r'^impressum/', 'main.impressum'),
    url(r'^editor/', 'main.editor'),
    url(r'^documents/', 'document.execute'),
    url(r'^projekt/', 'main.projekt'),
    url(r'^dateien/', 'main.dateien'),
    url(r'^vorlagen/', 'main.vorlagen'),
    url(r'^faq/', 'main.faq'),
    url(r'^favicon.png', RedirectView.as_view(url='/static/img/favicon.png')),
    url(r'^favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico')),
)
if settings.DEBUG:
    urlpatterns += patterns('app.views',
        (r'^documentPoster/', 'document.debug'),
    )
