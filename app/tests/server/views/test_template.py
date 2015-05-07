# -*- coding: utf-8 -*-
"""

* Purpose : Test des Template Views und zugehöriger Methoden (app/views/template.py)

* Creation Date : 26-11-2014

* Last Modified : Th 19 Feb 2015 21:07:00 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 3, 5

* Backlog entry : -

"""

from app.common.constants import ERROR_MESSAGES, DUPLICATE_NAMING_REGEX, DUPLICATE_INIT_SUFFIX_NUM
from app.common import util
from app.tests.server.views.viewtestcase import ViewTestCase
from app.models.folder import Folder
from app.models.projecttemplate import ProjectTemplate
from app.models.project import Project
from app.models.collaboration import Collaboration


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
        """Test der project2Template() Methode aus dem template view.
        
        Teste das konvertieren eines Projektes von einem Benutzer in eine Vorlage.
        
        Testfälle:
            - user1 konvertiert ein Projekt in ein Template -> Erfolg
            - user1 konvertiert ein Projekt in ein Template mit existierendem Namen
                    -> Erfolg (Name der erzeugten Vorlage mit Suffix '(2)')
            - user1 konvertiert ein Projekt in ein Template mit erneut dem Namen des vorherigen Testfalls
                    -> Erfolg (Name der erzeugten Vorlage mit Suffix '(3)')
            - user1 versucht ein Template mit Illegalen Zeichen zu erstellen -> Fehler
            - user1 versucht ein Template in ein Template zu verwandeln -> Fehler
            - user1 konvertiert ein freigegebenes Projekt
              (Einladung ist nicht bestätigt) in ein Template -> Fehler
            - user1 konvertiert ein freigegebenes Projekt
              (Einladung ist bestätigt) in ein Template -> Erfolg
        
        :return: None
        """

        # Sende Anfrage zum konvertieren eines vorhandenen Projektes in eine Vorlage
        response = util.documentPoster(
            self, command='project2template', idpara=self._user1_project1.id, name=self._newname1)

        templateobj = ProjectTemplate.objects.get(name=self._newname1, author=self._user1)

        # erwartete Antwort des Servers
        serveranswer = {'id': templateobj.id, 'name': self._newname1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Sende Anfrage zum konvertieren eines vorhandenen Projektes in eine Vorlage mit bereits existierendem Namen
        response = util.documentPoster(self, command='project2template',
                                       idpara=self._user1_project1.id, name=self._newname1)
        
        # erwartete Antwort des Servers
        serveranswer = {'id': ProjectTemplate.objects.get(author=self._user1,
                                                          name=DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM)).id,
                        'name': DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM)}

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Sende Anfrage zum konvertieren eines vorhandenen Projektes in eine Vorlage mit erneut dem Namen des vorherigen Testfalls
        response = util.documentPoster(self, command='project2template',
                                       idpara=self._user1_project1.id, name=self._newname1)
        
        # erwartete Antwort des Servers
        serveranswer = {'id': ProjectTemplate.objects.get(author=self._user1,
                                                          name=DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM+1)).id,
                        'name': DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM+1)}

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Teste, auf Namen mit illegalen Zeichen
        response = util.documentPoster(self, command='project2template', idpara=self._user1_project1.id, name='<>')

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Teste, ob man auch ein template in ein Template verwandeln kann
        # (sollte eine Fehlermeldung geben)
        response = util.documentPoster(self, command='project2template',
                                       idpara=self._user1_template1.id, name=self._newname2)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        collaboration = Collaboration.objects.create(project=self._user2_project1, user=self._user1)
        response = util.documentPoster(self, command='project2template', idpara=self._user2_project1.id, name=self._newname5)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])
        
        # --------------------------------------------------------------------------------------------------------------
        
        collaboration.isConfirmed = True
        collaboration.save()
        response = util.documentPoster(self, command='project2template', idpara=self._user2_project1.id, name=self._newname5)
        templateobj = ProjectTemplate.objects.get(name=self._newname5, author=self._user1)
        util.validateJsonSuccessResponse(self, response.content, {'id': templateobj.id, 'name': self._newname5})



    def test_template2Project(self):
        """Test der template2Project() Methode aus dem template view.

        Teste das konvertieren einer Vorlage von einem Benutzer in ein Projekt.

        Testfälle:
            - user1 konvertiert ein Template in ein Projekt -> Erfolg
            - user1 konvertiert ein Template in ein Projekt mit existierendem Namen
                    -> Erfolg (Name des erzeugten Projektes mit Suffix '(2)')
            - user1 konvertiert eine Vorlage in ein Projekt mit erneut dem Namen des vorherigen Testfalls
                    -> Erfolg (Name des erzeugten Projektes mit Suffix '(3)')
            - user1 versucht ein Projekt mit Illegalen Zeichen zu erstellen -> Fehler
            - user1 versucht ein Projekt in ein Projekt zu verwandeln -> Fehler

        :return: None
        """

        # Sende Anfrage zum konvertieren einer Vorlage in ein Projekt
        response = util.documentPoster(self, command='template2project', idpara=self._user1_template1.id,
                                       name=self._newname1)

        projectobj = Project.objects.filter(name=self._newname1, author=self._user1)[0]

        # erwartete Antwort des Servers
        serveranswer = {'id': projectobj.id, 'name': self._newname1, 'rootid': projectobj.rootFolder.id}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Sende Anfrage zum konvertieren einer Vorlage in ein Projekt mit bereits existierendem Namen
        response = util.documentPoster(self, command='template2project',
                                       idpara=self._user1_template1.id, name=self._newname1)
        
        projectobj = Project.objects.get(author=self._user1,
                                         name=DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM))
        
        # erwartete Antwort des Servers
        serveranswer = {'id': projectobj.id,
                        'name': DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM),
                        'rootid': projectobj.rootFolder.id}

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Sende Anfrage zum konvertieren einer Vorlage in ein Projekt mit erneut dem Namen des vorherigen Testfalls
        response = util.documentPoster(self, command='template2project',
                                       idpara=self._user1_template1.id, name=self._newname1)
        
        projectobj = Project.objects.get(author=self._user1,
                                         name=DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM+1))
        
        # erwartete Antwort des Servers
        serveranswer = {'id': projectobj.id,
                        'name': DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM+1),
                        'rootid': projectobj.rootFolder.id}

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Teste, auf Namen mit illegalen Zeichen
        response = util.documentPoster(self, command='template2project', idpara=self._user1_template1.id, name='<>')

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # Teste, ob man auch ein Projekt in ein Projekt verwandeln kann
        # (sollte eine Fehlermeldung geben)
        response = util.documentPoster(self, command='template2project', idpara=self._user1_project1.id,
                                       name=self._newname2)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['TEMPLATENOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

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

    def test_templateRename(self):
        """Test der templateRename() Methode aus dem project view

        Teste das Umbenennen einer Vorlage von einem Benutzer.

        Testfälle:
        - user1 benennt eine Vorlage um -> Erfolg
        - user1 benennt eine Vorlage um mit einem Namen, der nur Leerzeichen enthält -> Fehler
        - user1 benennt eine Vorlage um mit einem Namen, der nur ein leerer String ist -> Fehler
        - user1 benennt eine Vorlage um mit einem Namen, der ungültige Sonderzeichen enthält -> Fehler
        - user1 benennt eine Vorlage um mit einem Namen, der bereits existiert -> Fehler
        - user1 benennt eine Vorlage mit einer ungültigen projectid um -> Fehler
        - user1 benennt eine Vorlage von user2 um -> Fehler

        :return: None
        """

        # Sende Anfrage zum umbenennen einer Vorlage
        response = util.documentPoster(self, command='templaterename', idpara=self._user1_template1.id,
                                       name=self._newname1)

        # der neue Vorlagenname sollte in der Datenbank nun geändert worden sein
        self.assertEqual(ProjectTemplate.objects.get(id=self._user1_template1.id).name, self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_template1.id, 'name': self._newname1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit dictionary übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen einer Vorlage mit einem Namen der nur Leerzeichen enthält
        response = util.documentPoster(self, command='templaterename', idpara=self._user1_template2.id,
                                       name=self._name_only_spaces)

        # der Name der Vorlage sollte nicht mit name_only_spaces übereinstimmen
        self.assertNotEqual(ProjectTemplate.objects.get(id=self._user1_template2.id).name, self._name_only_spaces)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen einer Vorlage mit einem Namen der ein leerer String ist
        response = util.documentPoster(self, command='templaterename', idpara=self._user1_template2.id,
                                       name=self._name_blank)

        # der Name der Vorlage sollte nicht mit name_blank übereinstimmen
        self.assertNotEqual(ProjectTemplate.objects.get(id=self._user1_template2.id).name, self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen einer Vorlage mit einem Namen der ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='templaterename', idpara=self._user1_template2.id,
                                       name=self._name_invalid_chars)

        # der Name der Vorlage sollte nicht mit name_invalid_chars übereinstimmen
        self.assertNotEqual(ProjectTemplate.objects.get(id=self._user1_template2.id).name, self._name_invalid_chars)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen einer Vorlage mit einem Namen der bereits existiert
        response = util.documentPoster(self, command='templaterename', idpara=self._user1_template3.id,
                                       name=self._user1_template2.name.upper())

        # der Name der Vorlage sollte nicht mit template2.name.upper() übereinstimmen
        self.assertNotEqual(ProjectTemplate.objects.get(id=self._user1_template3.id).name,
                            self._user1_template2.name.upper())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['TEMPLATEALREADYEXISTS'] % self._user1_template2.name.upper()

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen einer Vorlage mit einer ungültigen template
        response = util.documentPoster(self, command='templaterename', idpara=self._invalidid,
                                       name=self._newname2)

        # es sollte keine Vorlage mit dem Namen newname2 vorhanden sein
        self.assertTrue(ProjectTemplate.objects.filter(name=self._newname2, author=self._user1).count() == 0)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['TEMPLATENOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen einer Vorlage mit einer templateid, welche user2 gehört
        response = util.documentPoster(self, command='templaterename', idpara=self._user2_template1.id,
                                       name=self._newname3)

        # der Name der Vorlage sollte nicht mit newname3 übereinstimmen
        self.assertNotEqual(ProjectTemplate.objects.get(id=self._user2_template1.id).name, self._newname3)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_listtemplates(self):
        """Test der listtemplates() Methode aus dem template view.

        Teste das Auflisten von Vorlagen eines Benutzers

        Testfälle:
            - user1 fordert eine Liste aller Vorlagen an -> Erfolg

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
            {
                "ownername": self._user1_template3.author.username,
                "rootid": self._user1_template3.rootFolder.id,
                "id": self._user1_template3.id,
                "createtime": util.datetimeToString(self._user1_template3.createTime),
                "ownerid": self._user1_template3.author.id,
                "name": self._user1_template3.name,
            },
        ]

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # teste, ob in response die beiden erstellten Vorlagen von user1 richtig aufgelistet werden
        # und keine Vorlagen von user2 aufgelistet werden
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)