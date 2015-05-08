# -*- coding: utf-8 -*-
"""

* Purpose : Test des Project Views und zugehöriger Methoden (app/views/project.py)

* Creation Date : 26-11-2014

* Last Modified : Do 26 Feb 2015 17:45:13 CET

* Author :  christian

* Coauthors : mattis, ingo, Kirill

* Sprintnumber : 2, 3, 5

* Backlog entry : -

"""

import zipfile
import shutil
import os
import mimetypes

from app.common.constants import ERROR_MESSAGES, ZIPMIMETYPE, DUPLICATE_NAMING_REGEX, DUPLICATE_INIT_SUFFIX_NUM
from app.common import util
from app.models.collaboration import Collaboration
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.plaintextfile import PlainTextFile
from app.tests.server.views.viewtestcase import ViewTestCase
from app.common.util import getUserModel
User = getUserModel()

class ProjectTestClass(ViewTestCase):
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

        # self.tearDownFiles()


    def test_projectCreate(self):
        """Test der projectCreate() Methode aus dem project view

        Teste das Erstellen eines neuen Projektes.

        Testfälle:
        - user1 erstellt ein neues Projekt -> Erfolg
        - user1 erstellt ein weiteres neues Projekt -> Erfolg
        - user1 erstellt ein Projekt, dessen Projektname nur Leerzeichen enthält -> Fehler
        - user1 erstellt ein Projekt, dessen Projektname ein leerer String ist -> Fehler
        - user1 erstellt ein Projekt, dessen Projektname ungültige Sonderzeichen enthält -> Fehler
        - user1 erstellt ein Projekt, dessen Projektname bereits existiert -> Erfolg (Name des erzeugten Projektes mit Suffix '(2)')
        - user1 erstellt ein weiteres Projekt mit dem Projektnamen des vorherigen Testfalls (Wiederholung des vorherigen Testfalls)
                -> Erfolg (Name des erzeugten Projektes mit Suffix '(3)')

        :return: None
        """

        # Sende Anfrage zum Erstellen eines neuen Projektes
        response = util.documentPoster(self, command='projectcreate', name=self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.filter(author=self._user1, name=self._newname1)[0].id,
                        'name': self._newname1}

        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Erstellen eines weiteren neuen Projektes
        response = util.documentPoster(self, command='projectcreate', name=self._newname2)

        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.filter(author=self._user1, name=self._newname2)[0].id,
                        'name': self._newname2}

        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name nur aus Leerzeichen besteht
        response = util.documentPoster(self, command='projectcreate', name=self._name_only_spaces)

        # es sollte kein Projekt mit dem Namen name_only_spaces in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._name_only_spaces, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name nur ein leerer String ist
        response = util.documentPoster(self, command='projectcreate', name=self._name_blank)

        # es sollte kein Projekt mit dem Namen name_blank in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._name_blank, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='projectcreate', name=self._name_invalid_chars)

        # es sollte kein Projekt mit dem Namen name_invalid_chars in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._name_invalid_chars, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        
        # erzeuge ein weiteres Projekt mit einem bereits existierenden Namen
        response = util.documentPoster(self, command='projectcreate', name=self._newname1)
        
        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.get(author=self._user1,
                                                  name=DUPLICATE_NAMING_REGEX % (self._newname1, DUPLICATE_INIT_SUFFIX_NUM)).id,
                        'name': DUPLICATE_NAMING_REGEX % (self._newname1, DUPLICATE_INIT_SUFFIX_NUM)}
        
        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        
        # erzeuge ein weiteres Projekt mit dem Namen des vorherigen Testfalls
        response = util.documentPoster(self, command='projectcreate', name=self._newname1)
        
        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.get(author=self._user1,
                                                  name=DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM+1)).id,
                        'name': DUPLICATE_NAMING_REGEX % (self._newname1,DUPLICATE_INIT_SUFFIX_NUM+1)}
        
        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
    
    
    def test_projectClone(self):
        """Test der projectClone() Methode aus dem project view

        Teste das Duplizieren eines Projektes.

        Testfälle:
        - user1 dupliziert ein vorhandenes Projekt -> Erfolg
        - user1 dupliziert ein nicht vorhandenens Projekt -> Fehler
        - user1 dupliziert ein Projekt, dessen Projektname nur Leerzeichen enthält -> Fehler
        - user1 dupliziert ein Projekt, dessen Projektname ein leerer String ist -> Fehler
        - user1 dupliziert ein Projekt, dessen Projektname ungültige Sonderzeichen enthält -> Fehler
        - user1 dupliziert ein Projekt, dessen Projektname bereits existiert -> Erfolg (Name des erzeugten Projektes mit Suffix '(2)')
        - user1 dupliziert das Projekt des vorherigen Testfalls erneut -> Erfolg (Name des erzeugten Projektes mit Suffix '(3)')
        - user1 dupliziert ein freigegebenes Projekt -> Erfolg

        :return: None
        """

        # Sende Anfrage zum Duplizieren eines Projektes
        response = util.documentPoster(self, command='projectclone', idpara=self._user1_project1.id,
                                       name=self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.filter(author=self._user1, name=self._newname1)[0].id,
                        'name': self._newname1}

        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())

        # --------------------------------------------------------------------------------------------------------------
        # dupliziere ein Projekt, mit einer ungültigen Id
        response = util.documentPoster(self, command='projectclone', idpara=self._invalidid,
                                       name=self._newname2)

        # es sollte kein Projekt mit dem Namen _newname2 in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._newname2, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # dupliziere ein Projekt, mit einem Namen der nur aus Leerzeichen besteht
        response = util.documentPoster(self, command='projectclone', idpara=self._user1_project2.id,
                                       name=self._name_only_spaces)

        # es sollte kein Projekt mit dem Namen name_only_spaces in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._name_only_spaces, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # dupliziere ein Projekt, mit einem Namen der nur ein leerer String ist
        response = util.documentPoster(self, command='projectclone', idpara=self._user1_project2.id,
                                       name=self._name_blank)

        # es sollte kein Projekt mit dem Namen name_blank in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._name_blank, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # dupliziere ein Projekt, mit einem Namen der ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='projectclone', idpara=self._user1_project2.id,
                                       name=self._name_invalid_chars)

        # es sollte kein Projekt mit dem Namen name_invalid_chars in der Datenbank vorhanden sein
        self.assertFalse((Project.objects.filter(name=self._name_invalid_chars, author=self._user1)))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        
        # dupliziere ein Projekt mit einem bereits existierenden Namen
        response = util.documentPoster(self, command='projectclone', idpara=self._user1_project2.id,
                                       name=self._user1_project2.name)
        
        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.get(author=self._user1,
                                                  name=DUPLICATE_NAMING_REGEX % (self._user1_project2.name,DUPLICATE_INIT_SUFFIX_NUM)).id,
                        'name': DUPLICATE_NAMING_REGEX % (self._user1_project2.name,DUPLICATE_INIT_SUFFIX_NUM)}
        
        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # dupliziere das Projekt des vorherigen Testfalls erneut
        response = util.documentPoster(self, command='projectclone', idpara=self._user1_project2.id,
                                       name=self._user1_project2.name)
        
        # erwartete Antwort des Servers
        serveranswer = {'id': Project.objects.get(author=self._user1,
                                                  name=DUPLICATE_NAMING_REGEX % (self._user1_project2.name,DUPLICATE_INIT_SUFFIX_NUM+1)).id,
                        'name': DUPLICATE_NAMING_REGEX % (self._user1_project2.name,DUPLICATE_INIT_SUFFIX_NUM+1)}
        
        # das erstellte Projekt sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']))
        # es sollte ein rootFolder angelegt worden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder)
        # die main.tex Datei sollte im Hauptverzeichnis vorhanden sein
        self.assertTrue(Project.objects.get(id=serveranswer['id']).rootFolder.getMainTex())
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        collaboration = Collaboration.objects.create(project=self._user2_project1, user=self._user1, isConfirmed=True)
        response = util.documentPoster(self, command='projectclone', idpara=self._user2_project1.id,
                                       name=self._newname3)
        projects = Project.objects.filter(name=self._newname3, author=self._user1)
        self.assertEqual(len(projects), 1)
        util.validateJsonSuccessResponse(self, response.content, {'id': projects[0].id, 'name': self._newname3})
    
    
    def test_projectRm(self):
        """Test der  projectRm() Methode aus dem project view

        Teste das Löschen eines Projektes von einem Benutzer.

        Testfälle:
        - user1 löscht ein vorhandenes Projekt -> Erfolg
        - user1 löscht ein nicht vorhandenes Projekt -> Fehler
        - user1 löscht ein Projekt welches user2 gehört -> Fehler

        :return: None
        """

        # Sende Anfrage zum Löschen eines vorhandenen Projektes
        response = util.documentPoster(self, command='projectrm', idpara=self._user1_project1.id)

        # es sollten keine Ordner des Projektes mehr in der Datenbank existieren
        self.assertFalse(Folder.objects.filter(id=self._user1_project1_folder1.id))
        self.assertFalse(Folder.objects.filter(id=self._user1_project1_folder2_subfolder1.id))

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines nicht vorhandenen Projektes
        response = util.documentPoster(self, command='projectrm', idpara=self._invalidid)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines Projektes von user2 (als user1)
        response = util.documentPoster(self, command='projectrm', idpara=self._user2_project1.id)

        # das Projekt sollte nicht gelöscht worden sein
        self.assertTrue(Project.objects.get(id=self._user2_project1.id))

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_projectRename(self):
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
        - user1 benennt ein Projekt um mit einem Namen, der bereits existiert -> Fehler
          (dieser Test dient der Überprüfung, ob richtig erkannt wird, dass ein Projekt mit Umlauten im Namen
           bereits existiert, bsp. Übungsprojekt 01 -> ÜBUNGSPROJEKT 01 sollte einen Fehler liefern)

        :return: None
        """

        # Sende Anfrage zum umbenennen eines Projektes
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project1.id,
                                       name=self._newname1)

        # der neue Projektname sollte in der Datenbank nun geändert worden sein
        self.assertEqual(Project.objects.get(id=self._user1_project1.id).name, self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_project1.id, 'name': self._newname1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit dictionary übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der nur Leerzeichen enthält
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project2.id,
                                       name=self._name_only_spaces)

        # der Name des Projektes sollte nicht mit name_only_spaces übereinstimmen
        self.assertNotEqual(Project.objects.get(id=self._user1_project2.id).name, self._name_only_spaces)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der ein leerer String ist
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project2.id,
                                       name=self._name_blank)

        # der Name des Projektes sollte nicht mit name_blank übereinstimmen
        self.assertNotEqual(Project.objects.get(id=self._user1_project2.id).name, self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project2.id,
                                       name=self._name_invalid_chars)

        # der Name des Projektes sollte nicht mit name_invalid_chars übereinstimmen
        self.assertNotEqual(Project.objects.get(id=self._user1_project2.id).name, self._name_invalid_chars)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der bereits existiert
        response = util.documentPoster(self, command='projectrename', idpara=self._user1_project3.id,
                                       name=self._user1_project2.name.upper())

        # der Name des Projektes sollte nicht mit project2.name.upper() übereinstimmen
        self.assertNotEqual(Project.objects.get(id=self._user1_project3.id).name, self._user1_project2.name.upper())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTALREADYEXISTS'] % self._user1_project2.name.upper()

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einer ungültigen projectid
        response = util.documentPoster(self, command='projectrename', idpara=self._invalidid,
                                       name=self._newname2)

        # es sollte kein Projekt mit dem Namen newname2 vorhanden sein
        self.assertTrue(Project.objects.filter(name=self._newname2, author=self._user1).count() == 0)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einer projectid, welche user2 gehört
        response = util.documentPoster(self, command='projectrename', idpara=self._user2_project1.id,
                                       name=self._newname3)

        # der Name des Projektes sollte nicht mit newname3 übereinstimmen
        self.assertNotEqual(Project.objects.get(id=self._user2_project1.id).name, self._newname3)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum umbenennen eines Projektes mit einem Namen der bereits existiert
        # Testet ob die Überprüfung auf Projekte mit dem selben Namen richtig funktioniert, wobei im Namen Umlaute sind
        # wird nur ausgeführt wenn keine SQLITE Datenbank benutzt wird, da dies sonst nicht unterstützt wird
        if not util.isSQLiteDatabse():
            response = util.documentPoster(self, command='projectrename', idpara=self._user1_project3.id,
                                           name=self._user1_project4.name.upper())

            # der Name des Projektes sollte nicht mit project4.name.upper() übereinstimmen
            self.assertNotEqual(Project.objects.get(id=self._user1_project3.id).name, self._user1_project4.name.upper())

            # erwartete Antwort des Servers
            serveranswer = ERROR_MESSAGES['PROJECTALREADYEXISTS'] % self._user1_project2.name.upper()

            # überprüfe die Antwort des Servers
            # status sollte failure sein
            # die Antwort des Servers sollte mit serveranswer übereinstimmen
            util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_listProjects(self):
        """Test der listprojects() Methode aus dem project view
        
        Teste das Auflisten aller Projekte eines Benutzers.
        
        Testfälle:
        - user1 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte nur Projekte von user1 beinhalten)
        - user2 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte nur Projekte von user2 beinhalten)
        - user3 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte leer sein)
        - user1 lädt user2 zum Projekt user1_project1 und
          user2 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte nur Projekte von user2 beinhalten)
        - user2 bestätigt die Kollaboration am Projekt user1_project1 und
                fordert eine Liste aller Projekte an -> Erfolg (Liste sollte alle Projekte von user2 und user1_project1 beinhalten)
        - user2 kündigt die Kollaboration am Projekt user1_project1 und
                fordert eine Liste aller Projekte an -> Erfolg (Liste sollte alle Projekte von user2 und
                                                                das neuerzeugte Duplikat von user1_project1 mit user2 als Autor beinhalten)
        
        :return: None
        """
        
        # Sende Anfrage zum Auflisten aller Projekte von user1
        response = util.documentPoster(self, command='listprojects')

        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user1_project1.id,
             'name': self._user1_project1.name,
             'ownerid': self._user1_project1.author.id,
             'ownername': self._user1_project1.author.username,
             'createtime': util.datetimeToString(self._user1_project1.createTime),
             'rootid': self._user1_project1.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user1_project2.id,
             'name': self._user1_project2.name,
             'ownerid': self._user1_project2.author.id,
             'ownername': self._user1_project2.author.username,
             'createtime': util.datetimeToString(self._user1_project2.createTime),
             'rootid': self._user1_project2.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user1_project3.id,
             'name': self._user1_project3.name,
             'ownerid': self._user1_project3.author.id,
             'ownername': self._user1_project3.author.username,
             'createtime': util.datetimeToString(self._user1_project3.createTime),
             'rootid': self._user1_project3.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user1_project4.id,
             'name': self._user1_project4.name,
             'ownerid': self._user1_project4.author.id,
             'ownername': self._user1_project4.author.username,
             'createtime': util.datetimeToString(self._user1_project4.createTime),
             'rootid': self._user1_project4.rootFolder.id,
             'collaboratorsnum': 0}
        ]

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # teste, ob in response die beiden erstellten Projekte von user1 richtig aufgelistet werden
        # und keine Projekte von user2 aufgelistet werden
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # logout von user1
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)

        # Sende Anfrage zum Auflisten aller Projekte von user2
        response = util.documentPoster(self, command='listprojects')

        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user2_project1.id,
             'name': self._user2_project1.name,
             'ownerid': self._user2_project1.author.id,
             'ownername': self._user2_project1.author.username,
             'createtime': util.datetimeToString(self._user2_project1.createTime),
             'rootid': self._user2_project1.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user2_project2.id,
             'name': self._user2_project2.name,
             'ownerid': self._user2_project2.author.id,
             'ownername': self._user2_project2.author.username,
             'createtime': util.datetimeToString(self._user2_project2.createTime),
             'rootid': self._user2_project2.rootFolder.id,
             'collaboratorsnum': 0}
        ]

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # teste, ob in response die beiden erstellten Projekte von user 2 richtig aufgelistet werden
        # und keine Projekte von user1 aufgelistet werden
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # logout von user2
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user3
        self.client.login(username=self._user3.username, password=self._user3._unhashedpw)

        # Sende Anfrage zum Auflisten aller Projekte von user3
        response = util.documentPoster(self, command='listprojects')

        # erwartete Antwort des Servers
        serveranswer = []

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # logout von user3
        self.client.logout()
        
        # --------------------------------------------------------------------------------------------------------------
        
        # login von user1
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)
        
        # user1 lädt user2 zum Projekt user1_project1 ein
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user2.username)
        
        # logout von user1
        self.client.logout()
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)
        
        # sende Anfrage zum Auflisten aller Projekte von user2
        response = util.documentPoster(self, command='listprojects')
        
        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user2_project1.id,
             'name': self._user2_project1.name,
             'ownerid': self._user2_project1.author.id,
             'ownername': self._user2_project1.author.username,
             'createtime': util.datetimeToString(self._user2_project1.createTime),
             'rootid': self._user2_project1.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user2_project2.id,
             'name': self._user2_project2.name,
             'ownerid': self._user2_project2.author.id,
             'ownername': self._user2_project2.author.username,
             'createtime': util.datetimeToString(self._user2_project2.createTime),
             'rootid': self._user2_project2.rootFolder.id,
             'collaboratorsnum': 0}
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # user2 bestätigt die Kollaboration am Projekt user1_project1
        util.documentPoster(self, command='activatecollaboration', idpara=self._user1_project1.id)
        
        # sende Anfrage zum Auflisten aller Projekte von user2
        response = util.documentPoster(self, command='listprojects')
        
        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user2_project1.id,
             'name': self._user2_project1.name,
             'ownerid': self._user2_project1.author.id,
             'ownername': self._user2_project1.author.username,
             'createtime': util.datetimeToString(self._user2_project1.createTime),
             'rootid': self._user2_project1.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user2_project2.id,
             'name': self._user2_project2.name,
             'ownerid': self._user2_project2.author.id,
             'ownername': self._user2_project2.author.username,
             'createtime': util.datetimeToString(self._user2_project2.createTime),
             'rootid': self._user2_project2.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user1_project1.id,
             'name': self._user1_project1.name,
             'ownerid': self._user1_project1.author.id,
             'ownername': self._user1_project1.author.username,
             'createtime': util.datetimeToString(self._user1_project1.createTime),
             'rootid': self._user1_project1.rootFolder.id,
             'collaboratorsnum': 1}
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # user2 kündigt die Kollaboration am Projekt user1_project1
        util.documentPoster(self, command='quitcollaboration', idpara=self._user1_project1.id)
        
        # sende Anfrage zum Auflisten aller Projekte von user2
        response = util.documentPoster(self, command='listprojects')
        
        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user2_project1.id,
             'name': self._user2_project1.name,
             'ownerid': self._user2_project1.author.id,
             'ownername': self._user2_project1.author.username,
             'createtime': util.datetimeToString(self._user2_project1.createTime),
             'rootid': self._user2_project1.rootFolder.id,
             'collaboratorsnum': 0},
            {'id': self._user2_project2.id,
             'name': self._user2_project2.name,
             'ownerid': self._user2_project2.author.id,
             'ownername': self._user2_project2.author.username,
             'createtime': util.datetimeToString(self._user2_project2.createTime),
             'rootid': self._user2_project2.rootFolder.id,
             'collaboratorsnum': 0},
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # logout von user2
        self.client.logout()


    def test_importZip(self):
        """Test der importZip() Methode aus dem project view

        Test das Importieren eines Projektes aus einer .zip Datei.

        Testfälle:
        - user1 importiert eine gültige zip Datei -> Erfolg
        - user1 importiert eine zip Datei die ungültige Dateien beinhaltet -> Fehler
        - user1 importiert eine ungültige/defekte zip Datei -> Fehler
        - user1 importiert eine gütlige zip Datei ohne Inhalt -> Fehler

        :return: None
        """

        # erstelle ein temp Verzeichnis
        tmpfolder = util.getNewTempFolder()

        # erstelle im temp Verzeichnis einen Projektordner und einige
        # Unterordner
        tmpfolder_project = os.path.join(tmpfolder, self._newname1)
        if not os.path.isdir(tmpfolder_project):
            os.mkdir(tmpfolder_project)
        if not os.path.isdir(os.path.join(tmpfolder_project, 'Ordner 1')):
            os.mkdir(os.path.join(tmpfolder_project, 'Ordner 1'))
        if not os.path.isdir(os.path.join(tmpfolder_project, 'Ordner 2')):
            os.mkdir(os.path.join(tmpfolder_project, 'Ordner 2'))
        if not os.path.isdir(os.path.join(tmpfolder_project, 'Ordner 1', 'Unterordner 1')):
            os.mkdir(
                os.path.join(tmpfolder_project, 'Ordner 1', 'Unterordner 1'))

        # erstelle die main.tex Datei im root Ordner des Projektes
        maintex = open(os.path.join(tmpfolder_project, 'main.tex'), 'w')
        maintex.write(self._new_code1)
        maintex.close()

        # Erstelle eine zip datei, die vom server angenommen werden sollte
        # erstelle eine zip Datei aus dem Projektordner
        zip_file_path = os.path.join(tmpfolder, (self._newname1 + '.zip'))
        util.createZipFromFolder(tmpfolder_project, zip_file_path)

        # stelle sicher, dass die zip Datei gültig ist
        self.assertTrue(zipfile.is_zipfile(zip_file_path))

        # lese die zip Datei ein und schreibe die Daten in den request
        zip_file = open(zip_file_path, 'rb')
        request = {
            'command': 'importzip',
            'files': [zip_file]
        }

        # Sende Anfrage zum Importieren der zip Datei
        response = self.client.post('/documents/', request)
        zip_file.close()

        projectobj = Project.objects.get(author=self._user1, name=self._newname1)

        # Teste, dass der Server eine positive Antwort geschickt hat
        serveranswer = {'id': projectobj.id, 'name': self._newname1, 'rootid': projectobj.rootFolder.id}
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # Teste, dass das Projekt existiert
        self.assertTrue(Project.objects.filter(author=self._user1, name=self._newname1).exists())
        projobj = Project.objects.get(author=self._user1, name=self._newname1)

        # Teste, dass eine main tex Datei existiert und diese den richtigen Inhalt hat
        self.assertTrue(PlainTextFile.objects.filter(name='main.tex', folder=projobj.rootFolder).exists())
        maintexobj = PlainTextFile.objects.get(name='main.tex', folder=projobj.rootFolder)
        self.assertEqual(maintexobj.source_code, self._new_code1)

        # Teste, dass auch Unterordner angelegt wurden
        self.assertTrue(Folder.objects.filter(name='Unterordner 1', root=projobj.rootFolder).exists())

        # lösche Projekt wieder
        Project.objects.get(author=self._user1, name=self._newname1).delete()
        # Teste, dass das Projekt nicht mehr existiert
        self.assertFalse(Project.objects.filter(author=self._user1, name=self._newname1).exists())

        # --------------------------------------------------------------------------------------------------------------
        # erstelle eine Binärdatei im Unterordner 1
        binfile = open(os.path.join(tmpfolder_project, 'Ordner 1', 'Unterordner 1', 'binary1.bin'), 'wb')
        binfile.write(os.urandom(128))
        binfile.close()

        # erstelle ine zip Datei, die vom Server nicht angenommen werden sollte,
        # da sie eine BinärDatei mit einem Mimetype enthält, welche nicht akzeptiert wird
        # erstelle eine zip Datei aus dem Projektordner
        zip_file_path = os.path.join(tmpfolder, (self._user1_project1.name + '.zip'))
        util.createZipFromFolder(tmpfolder_project, zip_file_path)

        # stelle sicher, dass die zip Datei gültig ist
        self.assertTrue(zipfile.is_zipfile(zip_file_path))

        # lese die zip Datei ein und schreibe die Daten in den request
        zip_file = open(zip_file_path, 'rb')
        request = {
            'command': 'importzip',
            'files': [zip_file]
        }

        # Sende Anfrage zum Importieren der zip Datei
        response = self.client.post('/documents/', request)
        zip_file.close()

        # Stelle sicher, dass das Projekt nicht mit dem Inhalt aus der zip Datei
        # überschrieben wurde
        self.assertFalse(Folder.objects.filter(root=self._user1_project1.rootFolder, name='Ordner 1'))


        # Die Binärdatei sollte eine ILLEGALFILETYPE Fehlermeldung hervorrufen
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['ILLEGALFILETYPE'] % "application/octet-stream"

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)


        # --------------------------------------------------------------------------------------------------------------
        # erstelle eine Datei mit zufälligem Inhalt (keine gültige zip Datei)
        zip_file_path = os.path.join(tmpfolder, (self._newname3 + '.zip'))
        zip_file = open(zip_file_path, 'a+b')
        zip_file.write(os.urandom(240))
        request = {
            'command': 'importzip',
            'files': [zip_file]
        }

        # Sende Anfrage zum Importieren der zip Datei
        response = self.client.post('/documents/', request)
        zip_file.close()

        # Stelle sicher, dass das Projekt auch nicht erstellt wurde
        self.assertFalse(Project.objects.filter(author=self._user1, name=self._newname3).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['EMPTYZIPFILE'] # TODO müsste eigentlich NOTAZIPFILE sein?!

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # erstelle eine zip Datei ohne Inhalt
        zip_file_path = os.path.join(tmpfolder, (self._newname4 + '.zip'))
        tmpfolder_project = os.path.join(tmpfolder, self._newname4)
        if not os.path.isdir(tmpfolder_project):
            os.makedirs(tmpfolder_project)
        util.createZipFromFolder(tmpfolder_project, zip_file_path)

        zip_file = open(zip_file_path, 'rb')
        # stelle sicher dass die leere Datei eine gültige zip Datei ist
        self.assertTrue(zipfile.is_zipfile(zip_file_path))

        request = {
            'command': 'importzip',
            'files': [zip_file]
        }

        # Sende Anfrage zum Importieren der zip Datei
        response = self.client.post('/documents/', request)
        zip_file.close()

        # Stelle sicher, dass das Projekt auch nicht erstellt wurde
        self.assertFalse(Project.objects.filter(author=self._user1, name=self._newname4).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['EMPTYZIPFILE']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # Lösche alle erstellten temporären Dateien und Verzeichnisse
        if os.path.isdir(tmpfolder):
            shutil.rmtree(tmpfolder)
        '''
        # --------------------------------------------------------------------------------------------------------------
        # Teste das zweimalige Importieren einer Zip mit Umlauten im namen
        for x in range(0,2):
            zip_file_path = self._zipfile1_path
            zip_file = open(zip_file_path, 'rb')
            # stelle sicher dass die leere Datei eine gültige zip Datei ist
            self.assertTrue(zipfile.is_zipfile(zip_file_path))

            request = {
                'command': 'importzip',
                'files': [zip_file]
            }
            # Sende Anfrage zum Importieren der zip Datei
            response = self.client.post('/documents/', request)
            zip_file.close()

            # Teste, dass der Server eine positive Antwort geschickt hat
            self.assertTrue(util.jsonDecoder(response.content))


            # Lösche alle erstellten temporären Dateien und Verzeichnisse
            if os.path.isdir(tmpfolder):
                shutil.rmtree(tmpfolder)
            '''

    def test_exportZip(self):
        """Test der exportZip() Methode des project view

        Teste das exportieren eines Projektes oder Ordners als .zip Datei.

        Testfälle:
        - user1 exportiert ein vorhandenes Projekt als zip Datei -> Erfolg
        - user1 exportiert einen vorhandenen Ordner als zip Datei -> Erfolg
        - user1 exportiert ein Projekt mit einer ungültigen rootFolderId -> Fehler
        - user1 exportiert ein Projekt mit einer rootFolderId, welche user2 gehört -> Fehler

        :return: None
        """

        # Sende Anfrage zum exportieren eines Projektes
        response = util.documentPoster(self, command='exportzip', idpara=self._user1_project1.rootFolder.id)

        # überprüfe die Antwort des Servers
        # Content-Type sollte application/zip sein
        self.assertEqual(response['Content-Type'], ZIPMIMETYPE)
        # Content-Length sollte mit gesendet worden sein
        self.assertIn('Content-Length', response)

        # erstelle temp Ordner
        tmpfolder = util.getNewTempFolder()
        tmpfolder_extracted = os.path.join(tmpfolder, 'extracted')
        if not os.path.isdir(tmpfolder_extracted):
            os.mkdir(tmpfolder_extracted)

        # Pfad zur temporären zip Datei
        tmp_zip_file = os.path.join(tmpfolder, (self._user1_project1.name + 'zip'))
        # Schreibe den Inhalt der empfangenen Datei in die temp zip Datei

        try:
            f = open(tmp_zip_file, 'a+b')
            f.write(response.content)
        finally:
            f.close()

        # überprüfe, ob es eine gültige zip Datei ist (magic number)
        self.assertTrue(zipfile.is_zipfile(tmp_zip_file))

        # entpacke die heruntergeladene Datei
        util.extractZipToFolder(tmpfolder_extracted, tmp_zip_file)

        # überprüfe ob der folder1 vorhanden ist
        self.assertTrue(os.path.isdir(os.path.join(tmpfolder_extracted, self._user1_project1_folder1.name)))
        # überprüfe ob der folder2_subfolder1 vorhanden ist
        folder2_subfolder1_path = os.path.join(tmpfolder_extracted, self._user1_project1_folder2.name,
                                               self._user1_project1_folder2_subfolder1.name)
        self.assertTrue(os.path.isdir(folder2_subfolder1_path))

        # überprüfe ob die main.tex Datei vorhanden ist
        maintex_path = os.path.join(tmpfolder_extracted, self._user1_tex1.name)
        self.assertTrue(os.path.isfile(maintex_path))

        # überprüfe, ob der Inhalt der main.tex Datei mit der Datenbank
        # übereinstimmt
        try:
            maintex = open(maintex_path, 'r')
            self.assertEqual(maintex.read(), self._user1_tex1.source_code)
        finally:
            maintex.close()

        # überprüfe ob binary1 vorhanden ist
        binary1_path = os.path.join(folder2_subfolder1_path, self._user1_binary1.name)
        self.assertTrue(os.path.isfile(binary1_path))

        # überprüfe ob binary2 vorhanden ist
        binary2_path = os.path.join(folder2_subfolder1_path, self._user1_binary2.name)
        self.assertTrue(os.path.isfile(binary2_path))

        # überprüfe ob binary3 vorhanden ist
        binary3_path = os.path.join(folder2_subfolder1_path, self._user1_binary3.name)
        self.assertTrue(os.path.isfile(binary3_path))

        # überprüfe ob der Inhalt der binary1 Datei mit der Datenbank übereinstimmt
        try:
            binfilecontent = self._user1_binary1.getContent()
            tmp_binary1 = open(binary1_path, 'rb')
            self.assertEqual(tmp_binary1.read(), binfilecontent.read())
            tmp_binary1.close()
        finally:
            binfilecontent.close()

        # Lösche die temporäre zip Datei und das temp Verzeichnis
        if os.path.isdir(tmpfolder):
            shutil.rmtree(tmpfolder)

        # --------------------------------------------------------------------------------------------------------------
        # sende Anfrage zum exportieren eines Ordners
        response = util.documentPoster(self, command='exportzip', idpara=self._user1_project1_folder2.id)

        # überprüfe die Antwort des Servers
        # Content-Type sollte application/zip sein
        self.assertEqual(response['Content-Type'], ZIPMIMETYPE)
        # Content-Length sollte mit gesendet worden sein
        self.assertIn('Content-Length', response)

        # erstelle temp Ordner
        tmpfolder = util.getNewTempFolder()
        tmpfolder_extracted = os.path.join(tmpfolder, 'extracted')
        if not os.path.isdir(tmpfolder_extracted):
            os.mkdir(tmpfolder_extracted)

        # Pfad zur temporären zip Datei
        tmp_zip_file = os.path.join(tmpfolder, (self._user1_project1.name + 'zip'))
        # Schreibe den Inhalt der empfangenen Datei in die temp zip Datei
        try:
            f = open(tmp_zip_file, 'a+b')
            f.write(response.content)
        finally:
            f.close()

        # überprüfe, ob es eine gültige zip Datei ist (magic number)
        self.assertTrue(zipfile.is_zipfile(tmp_zip_file))

        # entpacke die heruntergeladene Datei
        util.extractZipToFolder(tmpfolder_extracted, tmp_zip_file)

        # überprüfe ob der folder2_subfolder1 vorhanden ist
        folder2_subfolder1_path = os.path.join(tmpfolder_extracted, self._user1_project1_folder2_subfolder1.name)
        self.assertTrue(os.path.isdir(folder2_subfolder1_path))

        # überprüfe ob binary1 vorhanden ist
        binary1_path = os.path.join(folder2_subfolder1_path, self._user1_binary1.name)
        self.assertTrue(os.path.isfile(binary1_path))

        # überprüfe ob binary2 vorhanden ist
        binary2_path = os.path.join(folder2_subfolder1_path, self._user1_binary2.name)
        self.assertTrue(os.path.isfile(binary2_path))

        # überprüfe ob binary3 vorhanden ist
        binary3_path = os.path.join(folder2_subfolder1_path, self._user1_binary3.name)
        self.assertTrue(os.path.isfile(binary3_path))

        # überprüfe ob der Inhalt der binary1 Datei mit der Datenbank übereinstimmt
        try:
            binfilecontent = self._user1_binary1.getContent()
            tmp_binary1 = open(binary1_path, 'rb')
            self.assertEqual(tmp_binary1.read(), binfilecontent.read())
            tmp_binary1.close()
        finally:
            binfilecontent.close()

        # Lösche die temporäre zip Datei und das temp Verzeichnis
        if os.path.isdir(tmpfolder):
            shutil.rmtree(tmpfolder)

        # --------------------------------------------------------------------------------------------------------------
        # sende Anfrage zum exportieren eines Ordners mit einer ungültigen projectid
        response = util.documentPoster(self, command='exportzip', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)
        # es sollte keine Datei mitgesendet worden sein
        self.assertNotIn('Content-Disposition', response)
        # Content-Type sollte text/html sein
        self.assertEqual(response['Content-Type'], mimetypes.types_map['.html'])
        # Content-Length sollte nicht vorhanden sein
        self.assertNotIn('Content-Length', response)

        # --------------------------------------------------------------------------------------------------------------
        # sende Anfrage zum exportieren eines Projektes mit einer rootfolderID die user2 gehört (als user1)
        response = util.documentPoster(self, command='exportzip', idpara=self._user2_project1.rootFolder.id)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)
        # es sollte keine Datei mitgesendet worden sein
        self.assertNotIn('Content-Disposition', response)
        # Content-Type sollte text/html sein
        self.assertEqual(response['Content-Type'], mimetypes.types_map['.html'])
        # Content-Length sollte nicht vorhanden sein
        self.assertNotIn('Content-Length', response)


    def test_inviteUser(self):
        """Test der inviteUser()-Methode des project view
        
        Teste das Einladen eines Nutzers zur Kollaboration an einem Projekt.
        
        Testfälle:
        - user1 lädt sich selbst ein -> Fehler
        - user1 lädt unter Angabe einer leeren E-Mail-Adresse ein -> Fehler
        - user1 lädt einen nicht registrierten Nutzer ein -> Fehler
        - user1 lädt zu einem Projekt mit einer ungültigen Projekt-ID ein -> Fehler
        - user1 lädt einen registrierten, noch nicht zum betroffenen Projekt eingeladenen Nutzer user2 ein -> Erfolg
        - user1 lädt einen registrierten, bereits zum betroffenen Projekt eingeladenen Nutzer user2 ein -> Fehler
        - user2 lädt zu einem Projekt ein, für welches er nicht der Project-Owner ist -> Fehler

        :return: None
        """
        
        # sende Anfrage zum Einladen von sich selbst
        response = util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user1.username)
        
        # es sollte keine entsprechende Kollaboration mit Nutzer user1 und Projekt user1_project1 in der Datenbank vorhanden sein
        self.assertFalse(Collaboration.objects.filter(user=self._user1, project=self._user1_project1))
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['USERALREADYINVITED'] % self._user1.username
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # ermittelt Anzahl der Kollaborationen zum Projekt user1_project1
        count = Collaboration.objects.filter(project=self._user1_project1).count()
        
        # sende Anfrage zum Einladen eines Nutzers durch Angabe einer leeren E-Mail-Adresse
        response = util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name="")
        
        # es sollte keine Kollaboration für das Projekt user1_project1 in der Datenbank hinzugekommen sein
        self.assertTrue(Collaboration.objects.filter(project=self._user1_project1).count()==count)
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # teste, ob noch kein Nutzer mit der Kennung notregistered@latexweboffice.de registriert ist
        self.assertFalse(User.objects.filter(username="notregistered@latexweboffice.de"))
        
        # sende Anfrage zum Einladen eines nicht registrierten Nutzers
        response = util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name="notregistered@latexweboffice.de")
        
        not_registered_user = User.objects.create_user("notregistered@latexweboffice.de", "notregistered@latexweboffice.de", password="123456")
        # es sollte keine entsprechende Kollaboration mit Nutzer not_registered_user und Projekt user1_project1 in der Datenbank vorhanden sein
        self.assertFalse(Collaboration.objects.filter(user=not_registered_user, project=self._user1_project1))
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['USERNOTFOUND'] % "notregistered@latexweboffice.de"
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # ermittelt Anzahl der Kollaborationen mit Nutzer user2
        count = Collaboration.objects.filter(user=self._user2).count()
        
        # sende Anfrage zum Einladen zu einem Projekt mit einer ungültigen Projekt-ID
        response = util.documentPoster(self, command='inviteuser', idpara=self._invalidid, name=self._user2.username)
        
        # es sollte keine Kollaboration mit Nutzer user2 in der Datenbank hinzugekommen sein
        self.assertTrue(Collaboration.objects.filter(user=self._user2).count()==count)
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # teste, ob noch keine Kollaboration mit Nutzer user2 und Projekt user1_project1 vorhanden ist
        self.assertFalse(Collaboration.objects.filter(user=self._user2, project=self._user1_project1))
        
        # sende Anfrage zum Einladen eines noch nicht zum betroffenen Projekt eingeladenen Nutzers
        response = util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user2.username)
        
        # die entsprechende Kollaboration mit Nutzer user2 und Projekt user1_project1 sollte in der Datenbank vorhanden und abrufbar sein
        self.assertTrue(Collaboration.objects.get(user=self._user2, project=self._user1_project1))
        
        # erwartete Antwort des Servers
        serveranswer = {}
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # sende Anfrage zum Einladen eines bereits zum betroffenen Projekt eingeladenen Nutzers (Wiederholung der vorherigen Anfrage)
        response = util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user2.username)
        
        # es sollte genau eine entsprechende Kollaboration mit Nutzer user2 und Projekt user1_project1 in der Datenbank vorhanden sein
        self.assertTrue((Collaboration.objects.filter(user=self._user2, project=self._user1_project1)).count() == 1)
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['USERALREADYINVITED'] % self._user2.username
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # logout von user1
        self.client.logout()
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)
        
        # sende Anfrage zum Einladen zu einem Projekt, für welches der einladende Nutzer nicht der Project-Owner ist
        response = util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user3.username)
        
        # es sollte keine entsprechende Kollaboration mit Nutzer user3 und Projekt user1_project1 in der Datenbank vorhanden sein
        self.assertFalse(Collaboration.objects.filter(user=self._user3, project=self._user1_project1))
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # logout von user2
        self.client.logout()
    
    def test_listInvitedUsers(self):
        """Test der listInvitedUsers()-Methode aus dem project view
        
        Teste das Auflisten den Nutzernamen aller zu einem Projekt eingeladener Benutzer.
        
        Testfälle:
        - user1 fordert eine Liste aller zum Projekt user1_project1 eingeladener Benutzer an -> Erfolg (Liste sollte leer sein)
        - user1 lädt user3 zum Projekt user1_project1 ein und
                fordert eine Liste aller zum Projekt user1_project1 eingeladener Benutzer an -> Erfolg (Liste sollte ausschließlich user3 umfassen)
        - user1 lädt user2 zum Projekt user1_project1 ein und
                fordert eine Liste aller zum Projekt user1_project1 eingeladener Benutzer an -> Erfolg (Liste sollte in Reihenfolge user2 und user3 umfassen)
        - user1 fordert eine Liste aller eingeladener Benutzer zu einem Projekt mit einer ungültigen Projekt-ID an -> Fehler
        - user1 fordert eine Liste aller eingeladener Benutzer zu einem Projekt an, für welches er nicht der Project-Owner ist -> Fehler
        
        :return: None
        """
        
        # sende Anfrage zum Auflisten aller zum Projekt user1_project1 eingeladener Benutzer
        response = util.documentPoster(self, command='listinvitedusers', idpara=self._user1_project1.id)
        
        # erwartete Antwort des Servers
        serveranswer = []
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # user1 lädt user3 zum Projekt user1_project1 ein
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user3.username)
        
        # sende Anfrage zum Auflisten aller zum Projekt user1_project1 eingeladener Benutzer
        response = util.documentPoster(self, command='listinvitedusers', idpara=self._user1_project1.id)
        
        # erwartete Antwort des Servers
        serveranswer = [self._user3.username]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # user1 lädt user2 zum Projekt user1_project1 ein
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user2.username)
        
        # sende Anfrage zum Auflisten aller zum Projekt user1_project1 eingeladener Benutzer
        response = util.documentPoster(self, command='listinvitedusers', idpara=self._user1_project1.id)
        
        # erwartete Antwort des Servers
        serveranswer = [self._user2.username,
                        self._user3.username]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # sende Anfrage zum Auflisten aller zu einem Projekt mit einer ungültigen Projekt-ID eingeladener Benutzer
        response = util.documentPoster(self, command='listinvitedusers', idpara=self._invalidid)
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTNOTEXIST']
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # sende Anfrage zum Auflisten aller zu einem Projekt, für welches der aufrufende Nutzer nicht der Project-Owner ist
        response = util.documentPoster(self, command='listinvitedusers', idpara=self._user2_project1.id)
        
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']
        
        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        
    def test_listUnconfirmedCollaborativeProjects(self):
        """Test der listUnconfirmedCollaborativeProjects()-Methode aus dem project view
        
        Teste das Auflisten aller Projekte, zu deren Kollaboration ein Benutzer eingeladen ist, diese jedoch noch nicht bestätigt hat.
        
        Testfälle:
        - user1 fordert eine Liste aller unbestätigten Kollaborationsprojekte an -> Erfolg (Liste sollte leer sein)
        - user1 lädt user2 zum Projekt user1_project1 ein und
          user2 fordert eine Liste aller unbestätigten Kollaborationsprojekte an -> Erfolg (Liste sollte ausschließlich user1_project1 umfassen)
        - user1 lädt user3 zum Projekt user1_project1 ein und
          user3 fordert eine Liste aller unbestätigten Kollaborationsprojekte an -> Erfolg (Liste sollte ausschließlich user1_project1 umfassen)
        - user1 lädt user2 zu all seinen Projekten ein und
          user2 fordert eine Liste aller unbestätigten Kollaborationsprojekte an -> Erfolg (Liste sollte sämtliche Projekte von user1 umfassen)
        - user2 bestätigt die Kollaboration am Projekt user1_project1 und
                fordert eine Liste aller unbestätigten Kollaborationsprojekte an -> Erfolg (Liste sollte alle Projekte von user1
                                                                                            mit Ausnahme von user1_project1 umfassen)

        :return: None
        """
        
        # sende Anfrage zum Auflisten aller Projekte, zu deren Kollaboration user1 eingeladen ist, diese jedoch noch nicht bestätigt hat
        response = util.documentPoster(self, command='listunconfirmedcollaborativeprojects')
        
        # erwartete Antwort des Servers
        serveranswer = []
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # --------------------------------------------------------------------------------------------------------------
        
        # user1 lädt user2 zum Projekt user1_project1 ein
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user2.username)
        
        # logout von user1
        self.client.logout()
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)
        
        # sende Anfrage zum Auflisten aller Projekte, zu deren Kollaboration user2 eingeladen ist, diese jedoch noch nicht bestätigt hat
        response = util.documentPoster(self, command='listunconfirmedcollaborativeprojects')
        
        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user1_project1.id,
             'name': self._user1_project1.name,
             'ownerid': self._user1_project1.author.id,
             'ownername': self._user1_project1.author.username,
             'createtime': util.datetimeToString(self._user1_project1.createTime),
             'rootid': self._user1_project1.rootFolder.id,
             'collaboratorsnum': 1}
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # logout von user2
        self.client.logout()
        
        # --------------------------------------------------------------------------------------------------------------
        
        # login von user1
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)
        
        # user1 lädt user3 zum Projekt user1_project1 ein
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user3.username)
        
        # logout von user1
        self.client.logout()
        # login von user3
        self.client.login(username=self._user3.username, password=self._user3._unhashedpw)
        
        # sende Anfrage zum Auflisten aller Projekte, zu deren Kollaboration user3 eingeladen ist, diese jedoch noch nicht bestätigt hat
        response = util.documentPoster(self, command='listunconfirmedcollaborativeprojects')
        
        # erwartete Antwort des Servers
        serveranswer = [
            {'id': self._user1_project1.id,
             'name': self._user1_project1.name,
             'ownerid': self._user1_project1.author.id,
             'ownername': self._user1_project1.author.username,
             'createtime': util.datetimeToString(self._user1_project1.createTime),
             'rootid': self._user1_project1.rootFolder.id,
             'collaboratorsnum': 2}
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # logout von user3
        self.client.logout()
        
        # --------------------------------------------------------------------------------------------------------------
        
        # login von user1
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)
        
        # user1 lädt user2 zu all seinen Projekten ein
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project1.id, name=self._user2.username)
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project2.id, name=self._user2.username)
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project3.id, name=self._user2.username)
        util.documentPoster(self, command='inviteuser', idpara=self._user1_project4.id, name=self._user2.username)
        
        # logout von user1
        self.client.logout()
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)
        
        # sende Anfrage zum Auflisten aller Projekte, zu deren Kollaboration user2 eingeladen ist, diese jedoch noch nicht bestätigt hat
        response = util.documentPoster(self, command='listunconfirmedcollaborativeprojects')
        
        serveranswer = [
            {'id': self._user1_project1.id,
             'name': self._user1_project1.name,
             'ownerid': self._user1_project1.author.id,
             'ownername': self._user1_project1.author.username,
             'createtime': util.datetimeToString(self._user1_project1.createTime),
             'rootid': self._user1_project1.rootFolder.id,
             'collaboratorsnum': 2},
            {'id': self._user1_project2.id,
             'name': self._user1_project2.name,
             'ownerid': self._user1_project2.author.id,
             'ownername': self._user1_project2.author.username,
             'createtime': util.datetimeToString(self._user1_project2.createTime),
             'rootid': self._user1_project2.rootFolder.id,
             'collaboratorsnum': 1},
            {'id': self._user1_project3.id,
             'name': self._user1_project3.name,
             'ownerid': self._user1_project3.author.id,
             'ownername': self._user1_project3.author.username,
             'createtime': util.datetimeToString(self._user1_project3.createTime),
             'rootid': self._user1_project3.rootFolder.id,
             'collaboratorsnum': 1},
            {'id': self._user1_project4.id,
             'name': self._user1_project4.name,
             'ownerid': self._user1_project4.author.id,
             'ownername': self._user1_project4.author.username,
             'createtime': util.datetimeToString(self._user1_project4.createTime),
             'rootid': self._user1_project4.rootFolder.id,
             'collaboratorsnum': 1}
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
       
        # --------------------------------------------------------------------------------------------------------------
        
        # user2 bestätigt die Kollaboration am Projekt user1_project1
        util.documentPoster(self, command='activatecollaboration', idpara=self._user1_project1.id)
        
        # sende Anfrage zum Auflisten aller Projekte, zu deren Kollaboration user2 eingeladen ist, diese jedoch noch nicht bestätigt hat
        response = util.documentPoster(self, command='listunconfirmedcollaborativeprojects')
        
        serveranswer = [
            {'id': self._user1_project2.id,
             'name': self._user1_project2.name,
             'ownerid': self._user1_project2.author.id,
             'ownername': self._user1_project2.author.username,
             'createtime': util.datetimeToString(self._user1_project2.createTime),
             'rootid': self._user1_project2.rootFolder.id,
             'collaboratorsnum': 1},
            {'id': self._user1_project3.id,
             'name': self._user1_project3.name,
             'ownerid': self._user1_project3.author.id,
             'ownername': self._user1_project3.author.username,
             'createtime': util.datetimeToString(self._user1_project3.createTime),
             'rootid': self._user1_project3.rootFolder.id,
             'collaboratorsnum': 1},
            {'id': self._user1_project4.id,
             'name': self._user1_project4.name,
             'ownerid': self._user1_project4.author.id,
             'ownername': self._user1_project4.author.username,
             'createtime': util.datetimeToString(self._user1_project4.createTime),
             'rootid': self._user1_project4.rootFolder.id,
             'collaboratorsnum': 1}
        ]
        
        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
        
        # logout von user2
        self.client.logout()


    def test_activateCollaboration(self):
        """Test der activateCollaboration()-Methode aus dem project view

        Teste der Bestätigung einer Einladung zur Kollaboration an einem Projekt

        Testfälle:
        - Nicht existierende Kollaboration bestätigen -> COLLABORATIONNOTFOUND Fehler
        - user1 bestätigt die Kollaboration von user2 -> COLLABORATIONNOTFOUND Fehler
        - user1 bestätigt seine Kollaboration -> Erfolg

        :return: None
        """

        # Es gibt keine Kollaboration für das Projekt mit ID 1
        response = util.documentPoster(self, command='activatecollaboration', idpara=1)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['COLLABORATIONNOTFOUND'])


        collaboration = Collaboration.objects.create(user=self._user2, project=self._user1_project1)
        response = util.documentPoster(self, command='activatecollaboration', idpara=self._user1_project1.id)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['COLLABORATIONNOTFOUND'])
        self.assertFalse(Collaboration.objects.get(pk=collaboration.id).isConfirmed)


        collaboration2 = Collaboration.objects.create(user=self._user1, project=self._user2_project2)
        response = util.documentPoster(self, command='activatecollaboration', idpara=self._user2_project2.id)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertTrue(Collaboration.objects.get(pk=collaboration2.id).isConfirmed)


    def test_quitCollaboration(self):
        """Test der quitCollaboration()-Methode aus dem project view

        Teste der Kündigung der Kollaboration (bzw. Einladung) an einem Projekt

        Testfälle:
        - user1 kündigt die Kollaboration an seinem Projekt -> SELFCOLLABORATIONCANCEL Fehler
        - user1 kündigt der nicht bestätigten Einladung -> Erfolg
        - user1 kündigt der Kollaboration -> Erfolg

        :return: None
        """

        response = util.documentPoster(self, command='quitcollaboration', idpara=self._user1_project1.id)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['SELFCOLLABORATIONCANCEL'])


        # Kollaboration ist nicht bestätigt
        collaboration2 = Collaboration.objects.create(user=self._user1, project=self._user2_project2)
        response = util.documentPoster(self, command='quitcollaboration', idpara=self._user2_project2.id)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(Collaboration.objects.filter(pk=collaboration2.id).exists())
        # Es soll keine Kopie vom Projekt erstellt worden sein
        self.assertFalse(Project.objects.filter(author=self._user1, name=self._user2_project2.name).exists())


        collaboration3 = Collaboration.objects.create(user=self._user1, project=self._user2_project2)
        collaboration3.isConfirmed = True
        collaboration3.save()
        response = util.documentPoster(self, command='quitcollaboration', idpara=self._user2_project2.id)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(Collaboration.objects.filter(pk=collaboration3.id).exists())
        # Es soll keine Kopie vom Projekt erstellt worden sein
        self.assertFalse(Project.objects.filter(author=self._user1, name=self._user2_project2.name).exists())


    def test_cancelCollaboration(self):
        """Test der cancelCollaboration()-Methode aus dem project view

        Teste der Entziehung der Freigabe

        Testfälle:
        - user1 entzieht der Freigabe für nicht existierenden Nutzer -> COLLABORATIONNOTFOUND Fehler
        - user1 entzieht der Freigabe an seinem Projekt -> SELFCOLLABORATIONCANCEL Fehler
        - user1 entzieht der nicht bestätigten Freigabe -> Erfolg
        - user1 entzieht der bestätigten Freigabe -> Erfolg

        :return: None
        """

        response = util.documentPoster(self, command='cancelcollaboration', idpara=self._user1_project1.id, name='not@exists.com')
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['COLLABORATIONNOTFOUND'])


        response = util.documentPoster(self, command='cancelcollaboration', idpara=self._user1_project1.id, name=self._user1.username)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['SELFCOLLABORATIONCANCEL'])


        # Kollaboration ist nicht bestätigt
        collaboration = Collaboration.objects.create(user=self._user2, project=self._user1_project1)
        response = util.documentPoster(self, command='cancelcollaboration', idpara=self._user1_project1.id, name=self._user2.username)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(Collaboration.objects.filter(pk=collaboration.id).exists())
        self.assertFalse(Project.objects.filter(author=self._user2, name=self._user1_project1.name).exists())


        # Kollaboration ist bestätigt
        collaboration2 = Collaboration.objects.create(user=self._user2, project=self._user1_project2, isConfirmed=True)
        response = util.documentPoster(self, command='cancelcollaboration', idpara=self._user1_project2.id, name=self._user2.username)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(Collaboration.objects.filter(pk=collaboration2.id).exists())
        self.assertFalse(Project.objects.filter(author=self._user2, name=self._user1_project2.name).exists())
