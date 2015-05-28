LatexWebOffice
==============

[![Build Status](https://travis-ci.org/maltsev/LatexWebOffice.svg)](https://travis-ci.org/maltsev/LatexWebOffice)


### Abhängigkeiten
1. [Python 2.4](https://www.python.org/downloads/)
2. [virtualenv 1.7.2](https://github.com/pypa/virtualenv/)

### Installation (*nix)
1. Herunterlade [virtualenv 1.7.2](https://github.com/pypa/virtualenv/archive/1.7.2.zip)
2. Erzeuge eine isolierte Python-Umgebung: `python2.4 virtualenv-1.7.2/virtualenv.py venv`
3. Aktiviere die Umgebung: `source venv/bin/activate`
4. Installiere Python Module: `pip install -r requirements.txt`
5. Erzeuge die Datenbank: `python manage.py syncdb`