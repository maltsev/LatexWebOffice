LatexWebOffice
==============

[![Build Status](https://travis-ci.org/maltsev/LatexWebOffice.svg)](https://travis-ci.org/maltsev/LatexWebOffice) [![Coverage Status](https://coveralls.io/repos/maltsev/LatexWebOffice/badge.png?branch=dev)](https://coveralls.io/r/maltsev/LatexWebOffice?branch=dev)


### Abhängigkeiten
1. [Python 3.4+](https://www.python.org/downloads/)
2. [Django 1.7.1](https://www.djangoproject.com/)
3. [Python-magic](https://pypi.python.org/pypi/python-magic/)
4. [Einen Webserver](http://httpd.apache.org/)
5. [Einen Pythonapplikationserver (apache mod wsgi, gunicorn, ...)](https://code.google.com/p/modwsgi/) 
6. [Mysql](http://www.mysql.de/)

Grundsätzlich kann LatexWebOffice auch ohne Webserver, Pythonappliaktionserver und Mysql verwendet werden. In diesem Falle kann der Developerserver von Django verwendet werden. Dieser Modus ist jedoch für Produktivsystemen nicht zu empfehlen.

### Installation
1. klone das Projekte in einen beliebigen Ordner
2. passe core/latexwebofficeconf.py mit den Daten der eigenen Datenbank und smptp Server an
3. passe core/wsgi.py anhand des verwendeten Pythonservers an

### Beispielkonfiguration
In dieser Beispielkonfiguration wird davon ausgegangen, dass LatexWebOffice in /var/www/LatexWebOffice installiert wurde.
## Mysql
Es wird ein user und Datenbank mit dem Namen latexweboffice erstellt. Der user latexweboffice hat volle Rechte auf die Datenbank gleichen Namens. Das Passwort für den user lautet '123456'.

```
create database latexweboffice;
grant usage on *.* to latexweboffice@localhost identified by '123456';
grant all privileges on latexweboffice.* to latexweboffice@localhost ;
```

## Apache Einstellungen mit WSGI
# Apache
Beispielkonfiguration für Apache um LatexWebOffice als Hauptdomain auf Port 80 zu nutzen. [Apache Dokumentation](http://httpd.apache.org/docs/2.2/de/configuring.html#main) für genauere Anweisungen.  
```
Alias /static/ /var/www/LatexWebOffice/app/static/

<Directory "/var/www/LatexWebOffice/app/static">
	Require all granted
	Options  +Indexes
</Directory>

# http://blog.dscpl.com.au/2014/09/setting-lang-and-lcall-when-using.html
WSGIDaemonProcess latexweboffice lang='de_DE.UTF-8' locale='de_DE.UTF-8' python-path=/home/latexweboffice/Env/python3webofficeenv/lib/python3.4/site-packages
WSGIProcessGroup latexweboffice        
WSGIScriptAlias / /var/www/LatexWebOffice/core/wsgi.py

<Directory "/var/www/LatexWebOffice/core">
	<Files wsgi.py>
		Require all granted
	</Files>
</Directory>
```
# core/wsgi.py
```
import sys
sys.path.append('/var/www/LatexWebOffice')
```
Anschließend müssen die Datenbanktabellen für LatexWebOffice erstellt werden.

```
python manage.py migrate
```
Zum Schluss muss Apache neugestartet werden.
