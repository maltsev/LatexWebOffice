from django.conf.urls import patterns, include, url
from django.contrib import admin
import app.urls

urlpatterns = app.urls.urlpatterns + patterns('',
    url(r'^admin/', include(admin.site.urls)),
)