from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import app.urls

admin.autodiscover()

urlpatterns = app.urls.urlpatterns + patterns('',
    url(r'^admin/', include(admin.site.urls)),
) + staticfiles_urlpatterns()
