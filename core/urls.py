# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.conf import settings
import app.urls

urlpatterns = app.urls.urlpatterns + patterns('',
    url(r'^admin/', include(admin.site.urls)),
) + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
