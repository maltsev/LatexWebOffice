LatexWebOffice
==============

[![Build Status](https://travis-ci.org/Moeplhausen/LatexWebOffice.svg)](https://travis-ci.org/Moeplhausen/LatexWebOffice) [![Coverage Status](https://coveralls.io/repos/Moeplhausen/LatexWebOffice/badge.png?branch=dev)](https://coveralls.io/r/Moeplhausen/LatexWebOffice?branch=dev)


### Abhängigkeiten
1. [Python 3.4+](https://www.python.org/downloads/)
2. [Python-magic](https://pypi.python.org/pypi/python-magic/)
3. [Einen Webserver](http://httpd.apache.org/)
4. [Einen Pythonapplikationserver (apache mod wsgi, gunicorn, ...)](https://code.google.com/p/modwsgi/) 
5. [Mysql](http://www.mysql.de/)

### Installation
1. klone das Projekte in einen beliebigen Ordner
2. passe core/latexwebofficeconf.py mit den Daten der eigenen Datenbank an
3. passe core/wsgi.py anhand des verwendeten Pythonservers an



### Beispielkonfiguration
## Mysql
Es wird ein user und Datenbank mit dem Namen latexweboffice erstellt. Der user latexweboffice hat volle Rechte auf die Datenbank gleichen Namens. Das Passwort für den user lautet '123456'.

```
create database latexweboffice;
grant usage on *.* to latexweboffice@localhost identified by '123456';
grant all privileges on latexweboffice.* to latexweboffice@localhost ;
```

## Apache mit wsgi
# apache
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
# wsgi.py
```
import sys
sys.path.append('/var/www/LatexWebOffice')
```
