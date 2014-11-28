"""

* Purpose : Test der Dokument- und Projektverwaltung (app/view/documents.py)

* Creation Date : 20-11-2014

* Last Modified : Mi 26 Nov 2014 14:58:13 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : -

"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common import util
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from django.conf import settings
import os, json


class DocumentsTestClass(TestCase):
    # Initialiserung der benötigten Objecte
    # -> wird vor jedem Test ausgeführt
    def setUp(self):
        # erstelle user1
        self._user1 = User.objects.create_user(
            username='user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass


    # Teste die Verteilfunktion, die die verschiedenen Document-commands den richtigen Methode zuweist
    def test_Execute(self):
        missingpara_id = {'name': 'id', 'type': int}
        missingpara_content = {'name': 'content', 'type': str}
        missingpara_name = {'name': 'name', 'type': str}

        # Teste Aufruf mit fehlendem Parameter
        # createdir command benötigt Parameter 'id':parentdirid und 'name':
        # directoryname
        response = util.documentPoster(self, command='createdir', idpara=None, name='newfolder')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['MISSINGPARAMETER'] liefern
        util.validateJsonFailureResponse(
            self, response.content,
            ERROR_MESSAGES['MISSINGPARAMETER'].format(missingpara_id)
        )

        # Teste unbekannten Befehl ('command')
        response = util.documentPoster(self, command='DOESNOTEXIST')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern, da der Parameter 'DOESNOTEXIST' nicht existiert
        # sollte die Fehlermeldung ERROR_MESSAGES['COMMANDNOTFOUND'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['COMMANDNOTFOUND'])

        # Teste Fehlerhafte Parameter:
        # id!=int
        response = util.documentPoster(self, command='createdir', idpara='noIntID', name='newfolder')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern, da ein String als ID übergeben wurde
        # sollte die Fehlermeldung ERROR_MESSAGES['MISSINGPARAMETER'] liefern
        util.validateJsonFailureResponse(self, response.content,
                                         ERROR_MESSAGES['MISSINGPARAMETER'].format(missingpara_id))

        # files!=files
        # TODO