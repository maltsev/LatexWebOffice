# -*- coding: utf-8 -*-
"""

* Purpose : Test der Dokument- und Projektverwaltung (app/view/documents.py)

* Creation Date : 20-11-2014

* Last Modified : Mi 26 Nov 2014 14:58:13 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : -

"""

from app.common.constants import ERROR_MESSAGES
from app.common import util
from app.tests.server.views.viewtestcase import ViewTestCase


class DocumentsTestClass(ViewTestCase):
    def setUp(self):
        """Setup Methode für die einzelnen Tests

         Diese Funktion wird vor jeder Testfunktion ausgeführt.
         Damit werden die notwendigen Variablen und Modelle für jeden Test neu initialisiert.
         Die Methoden hierzu befinden sich im ViewTestCase (viewtestcase.py).

        :return: None
        """

        self.setUpSingleUser()

    def tearDown(self):
        """Freigabe von nicht mehr notwendigen Ressourcen.

        Diese Funktion wird nach jeder Testfunktion ausgeführt.

        :return: None
        """

        pass



    def test_Execute(self):
        """Test der execute() Methode des document view

        Teste die Verteilfunktion, die die verschiedenen Document-commands den richtigen Methode zuweist.

        Testfälle:
        - user1 ruft createdir mit fehlendem Parameter id auf -> Fehler
        - user1 ruft unbekannten Befehl auf -> Fehler
        - user1 ruft createdir mit eine String als id auf -> Fehler
        - user1 ruft updatefile auf ohne den content mitzusenden -> Fehler

        :return: None
        """

        missingpara_id = {'name': 'id', 'type': int}
        missingpara_content = {'name': 'content', 'type': str}
        missingpara_name = {'name': 'name', 'type': str}

        # Teste Aufruf mit fehlendem Parameter
        # createdir command benötigt Parameter 'id':parentdirid und 'name': directoryname
        response = util.documentPoster(self, command='createdir', idpara=None, name='newfolder')

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['MISSINGPARAMETER'] % missingpara_id

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Teste unbekannten Befehl ('command')
        response = util.documentPoster(self, command='DOESNOTEXIST')

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['COMMANDNOTFOUND']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen eines Ordners mit einem String als ID
        response = util.documentPoster(self, command='createdir', idpara='noIntID', name='newfolder')

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['MISSINGPARAMETER'] % missingpara_id

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum ändern des Inhalt einer .tex Datei ohne den Inhalt mitzusenden
        response = util.documentPoster(self, command='updatefile', idpara=1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['MISSINGPARAMETER'] % missingpara_content

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        #util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer Datei ohne den neuen Namen mitzusenden
        response = util.documentPoster(self, command='renamefile', idpara=1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['MISSINGPARAMETER'] % missingpara_name

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        #util.validateJsonFailureResponse(self, response.content, serveranswer)