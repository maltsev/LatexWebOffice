"""

* Purpose : Test des Template Views und zugehöriger Methoden (app/views/template.py)

* Creation Date : 26-11-2014

* Last Modified : Fr 19 Dez 2014 08:10:32 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 3

* Backlog entry : -

"""

from app.common.constants import ERROR_MESSAGES
from app.common import util
from app.tests.server.viewtestcase import ViewTestCase
from app.models.folder import Folder
from app.models.projecttemplate import ProjectTemplate
from app.models.project import Project


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
            - user1 konvertiert ein Projekt in ein Template => Erfolg
            - user1 versucht ein Template mit existierenden Namen zu erstellen
            => Fehler
            - user1 versucht ein Template mit Illegalen Zeichen zu erstellen =>
            Fehler
            - user1 versucht ein Template in ein Template zu verwandeln =>
            Fehler


        :return: None
        """

        # Sende Anfrage zum konvertieren eines vorhandenen Projektes in eine
        # Vorlage
        response = util.documentPoster(
            self, command='project2template', idpara=self._user1_project1.id, name=self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {'id': 9, 'name': 'NeuerName1'}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # Versuche ein template mit zweimal den gleichen Namen zu erstellen
        # (sollte eine Fehlermeldung hervorrufen)
        response = util.documentPoster(
            self, command='project2template', idpara=self._user1_project1.id, name=self._newname1)
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['TEMPLATEALREADYEXISTS'].format(
            self._newname1)
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # Teste, auf Namen mit illegalen Zeichen
        response = util.documentPoster(
            self, command='project2template', idpara=self._user1_project1.id, name='<>')
        serveranswer = ERROR_MESSAGES['INVALIDNAME']
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # Teste, ob man auch ein template in ein Template verwandeln kann
        # (sollte eine Fehlermeldung geben)
        response = util.documentPoster(
            self, command='project2template', idpara=self._user1_template1.id, name=self._newname2)
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']
        util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_template2Project(self):
        """Test der template2Project() Methode aus dem template view

        Teste das konvertieren einer Vorlage von einem Benutzer in ein Projekt.

        Testfälle:
            - user1 konvertiert ein Template in ein Projekt => Erfolg
            - user1 versucht ein Projekt mit existierenden Namen zu erstellen
            => Fehler
            - user1 versucht ein Projekt mit Illegalen Zeichen zu erstellen =>
            Fehler
            - user1 versucht ein Projekt in ein Projekt zu verwandeln =>
            Fehler


        :return: None
        """

        # Sende Anfrage zum konvertieren einer Vorlage in ein Projekt
        response = util.documentPoster(
            self, command='template2project', idpara=self._user1_template1.id, name=self._newname1)

        projectobj = Project.objects.filter(name=self._newname1, author=self._user1)[0]

        # erwartete Antwort des Servers
        serveranswer = {'id': projectobj.id, 'name': self._newname1, 'rootid': projectobj.rootFolder.id}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # Versuche ein template mit zweimal den gleichen Namen zu erstellen
        # (sollte eine Fehlermeldung hervorrufen)
        response = util.documentPoster(
            self, command='template2project', idpara=self._user1_template1.id, name=self._newname1)
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(
            self._newname1)
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # Teste, auf Namen mit illegalen Zeichen
        response = util.documentPoster(
            self, command='template2project', idpara=self._user1_template1.id, name='<>')
        serveranswer = ERROR_MESSAGES['INVALIDNAME']
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # Teste, ob man auch ein Projekt in ein Projekt verwandeln kann
        # (sollte eine Fehlermeldung geben)
        response = util.documentPoster(
            self, command='template2project', idpara=self._user1_project1.id, name=self._newname2)
        serveranswer = ERROR_MESSAGES['TEMPLATENOTEXIST']
        util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_listtemplates(self):
        """Test der listtemplates() Methode aus dem template view

        Teste das Auflisten von Vorlagen eines Benutzers

        Testfälle:
            - user1 fordert eine Liste aller Projekte an -> Erfolg

        :returns: None

        """
        # Sende Anfrage zum Auflisten aller Vorlagen
        response = util.documentPoster(
            self, command='listtemplates')

        # erwartete Antwort des Servers
        serveranswer = [
            {
                "ownername": self._user1_template1.author.username,
                "rootid": self._user1_template1.rootFolder.id,
                "id": self._user1_template1.id,
                "createtime": util.datetimeToString(self._user1_template1.createTime),
                "ownerid": self._user1_template1.author.id,
                "name": self._user1_template1.name,
            },
            {
                "ownername": self._user1_template2.author.username,
                "rootid": self._user1_template2.rootFolder.id,
                "id": self._user1_template2.id,
                "createtime": util.datetimeToString(self._user1_template2.createTime),
                "ownerid": self._user1_template2.author.id,
                "name": self._user1_template2.name,
            },
        ]

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # teste, ob in response die beiden erstellten Vorlagen von user1 richtig aufgelistet werden
        # und keine Vorlagen von user2 aufgelistet werden
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

    def test_templateRm(self):
        """Test der templateRm() Methode aus dem template view

        Teste das Löschen einer Vorlage von einem Benutzer.

        Testfälle:
        - user1 löscht eine vorhandene Vorlage -> Erfolg
        - user1 löscht eine nicht vorhandene Vorlage -> Fehler
        - user1 löscht eine Vorlage welche user2 gehört -> Fehler

        :return: None
        """

        # Sende Anfrage zum Löschen einer vorhandenen Vorlage
        response = util.documentPoster(self, command='templaterm', idpara=self._user1_template1.id)

        # es sollten keine Ordner der Vorlage mehr in der Datenbank existieren
        self.assertFalse(Folder.objects.filter(id=self._user1_template1_folder1.id))
        self.assertFalse(Folder.objects.filter(id=self._user1_template1_folder2_subfolder1.id))

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines nicht vorhandenen Projektes
        response = util.documentPoster(self, command='templaterm', idpara=self._invalidid)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['TEMPLATENOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines Projektes von user2 (als user1)
        response = util.documentPoster(self, command='templaterm', idpara=self._user2_template1.id)

        # das Projekt sollte nicht gelöscht worden sein
        self.assertTrue(ProjectTemplate.objects.get(id=self._user2_template1.id))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)