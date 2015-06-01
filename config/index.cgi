#!/usr/bin/python
# Quelle: http://django.readthedocs.org/en/1.3.X/howto/deployment/fastcgi.html

import sys, os

# Verzeichnis mit dem LWO-Quellkode
lwo_path = '/www/data/IVV5LWO/latexweboffice'
sys.path.insert(0, lwo_path)

# Verzeichnis mit der Python-Umgebung
sys.path.insert(0, '/www/data/IVV5LWO/venv/lib64/python2.4/site-packages')

os.chdir(lwo_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Importiere einige Funktionen, die in Python 2.4.3 und in Django 1.3.7 fehlen
import compatibility

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method='threaded', daemonize='false')