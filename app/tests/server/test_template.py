"""

* Purpose : Test des Template Views und zugehöriger Methoden (app/views/template.py)

* Creation Date : 26-11-2014

* Last Modified : Mo 15 Dez 2014 14:50:33 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 3

* Backlog entry : -

"""

from app.common.constants import ERROR_MESSAGES
from app.common import util
from app.tests.server.viewtestcase import ViewTestCase


class TemplateTestClass(ViewTestCase):

    def setUp(self):
        """Setup Methode für die einzelnen Tests

         Diese Funktion wird vor jeder Testfunktion ausgeführt.
         Damit werden die notwendigen Variablen und Modelle für jeden Test neu initialisiert.
         Die Methoden hierzu befinden sich im ViewTestCase (viewtestcase.py).

        :return: None
        """

        self.setUpUserAndProjects()
        self.setUpFolders()
        self.setUpFiles()
        self.setUpValues()

    def tearDown(self):
        """Freigabe von nicht mehr notwendigen Ressourcen.

        Diese Funktion wird nach jeder Testfunktion ausgeführt.

        :return: None
        """

        self.tearDownFiles()

    def test_project2Template(self):
        """Test der project2Template() Methode aus dem template view

        Teste das konvertieren eines Projektes von einem Benutzer in eine Vorlage.

        Testfälle:

        :return: None
        """

        # Sende Anfrage zum konvertieren eines vorhandenen Projektes in eine
        # Vorlage
        '''response = util.documentPoster(
            self, command='project2template', idpara=self._user1_project1.id,name=self._newname1)
        '''

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        #util.validateJsonSuccessResponse(self, response.content, serveranswer)

    def atest_projectRename(self):
        """Test der projectRename() Methode aus dem project view

        Teste das Umbenennen eines Projektes von einem Benutzer.

        Testfälle:
        - user1 benennt ein Projekt um -> Erfolg
        - user1 benennt ein Projekt um mit einem Namen, der nur Leerzeichen enthält -> Fehler
        - user1 benennt ein Projekt um mit einem Namen, der nur ein leerer String ist -> Fehler
        - user1 benennt ein Projekt um mit einem Namen, der ungültige Sonderzeichen enthält -> Fehler
        - user1 benennt ein Projekt um mit einem Namen, der bereits existiert -> Fehler
        - user1 benennt ein Projekt mit einer ungültigen projectid um -> Fehler
        - user1 benennt ein Projekt von user2 um -> Fehler

        :return: None
        """

        # Sende Anfrage zum umbenennen eines Projektes
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project1.id,
                                       name=self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_project1.id, 'name': self._newname1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit dictionary übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der nur
        # Leerzeichen enthält
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project2.id,
                                       name=self._name_only_spaces)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der ein
        # leerer String ist
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project2.id,
                                       name=self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der
        # ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project2.id,
                                       name=self._name_invalid_chars)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der
        # bereits existiert
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project3.id,
                                       name=self._user1_project2.name.upper())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(
            self._user1_project2.name.upper())

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einer ungültigen
        # projectid
        response = util.documentPoster(self, command='projectrename', idpara=self._invalidid,
                                       name=self._newname2)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einer projectid,
        # welche user2 gehört
        response = util.documentPoster(self, command='projectrename', idpara=self._user2_project1.id,
                                       name=self._newname3)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
