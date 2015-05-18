#!/usr/bin/python
# Quelle: http://django.readthedocs.org/en/1.3.X/howto/deployment/fastcgi.html#running-django-on-a-shared-hosting-provider-with-apache

import sys, os

# Verzeichnis mit dem LWO-Quellkode
lwo_path = '/www/data/IVV5LWO/latexweboffice'
# Verzeichnis mit der Python-Umgebung
virtualenv_path = '/www/data/IVV5LWO/venv'

sys.path.insert(0, os.path.join(virtualenv_path, 'lib64/python2.4/site-packages'))
sys.path.insert(0, lwo_path)

os.chdir(lwo_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Importiere einige Funktionen, die in Python 2.4.3 und in Django 1.3.7 fehlen
import compatibility

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')