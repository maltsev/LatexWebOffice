"""

* Purpose : Test des Project Views und zugehöriger Methoden (app/views/project.py)

* Creation Date : 26-11-2014

* Last Modified : Fr 19 Dez 2014 11:15:20 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2, 3

* Backlog entry : -

"""

import zipfile
import shutil
import os
import mimetypes

from app.common.constants import ERROR_MESSAGES, SUCCESS
from app.common import util
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.plaintextfile import PlainTextFile
from app.tests.server.viewtestcase import ViewTestCase


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

        #self.tearDownFiles()


    def test_projectCreate(self):
        """Test der projectCreate() Methode aus dem project view

        Teste das Erstellen eines neuen Projektes.

        Testfälle:
        - user1 erstellt ein neues Projekt -> Erfolg
        - user1 erstellt ein weiteres neues Projekt -> Erfolg
        - user1 erstellt ein Projekt, dessen Projektname nur Leerzeichen enthält -> Fehler
        - user1 erstellt ein Projekt, dessen Projektname ein leerer String ist -> Fehler
        - user1 erstellt ein Projekt, dessen Projektname ungültige Sonderzeichen enthält -> Fehler
        - user1 erstellt ein Projekt, dessen Projektname bereits existiert -> Fehler

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
        response = util.documentPoster(self, command='projectcreate', name=self._newname1.upper())

        # es sollte nur ein Projekt mit dem Namen newname1 in der Datenbank vorhanden sein
        self.assertTrue((Project.objects.filter(name=self._newname1, author=self._user1)).count() == 1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(self._newname1.upper())

        # überprüfe die Antwort des Server
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

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
        serveranswer = ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(self._user1_project2.name.upper())

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

    def test_listProjects(self):
        """Test der listprojects() Methode aus dem project view

        Teste das Auflisten aller Projekte eines Benutzers.

        Testfälle:
        - user1 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte nur Projekte von user1 beinhalten)
        - user2 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte nur Projekte von user2 beinhalten)
        - user3 fordert eine Liste aller Projekte an -> Erfolg (Liste sollte leer sein)

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
             'rootid': self._user1_project1.rootFolder.id},
            {'id': self._user1_project2.id,
             'name': self._user1_project2.name,
             'ownerid': self._user1_project2.author.id,
             'ownername': self._user1_project2.author.username,
             'createtime': util.datetimeToString(self._user1_project2.createTime),
             'rootid': self._user1_project2.rootFolder.id},
            {'id': self._user1_project3.id,
             'name': self._user1_project3.name,
             'ownerid': self._user1_project3.author.id,
             'ownername': self._user1_project3.author.username,
             'createtime': util.datetimeToString(self._user1_project3.createTime),
             'rootid': self._user1_project3.rootFolder.id}
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
             'rootid': self._user2_project1.rootFolder.id},
            {'id': self._user2_project2.id,
             'name': self._user2_project2.name,
             'ownerid': self._user2_project2.author.id,
             'ownername': self._user2_project2.author.username,
             'createtime': util.datetimeToString(self._user2_project2.createTime),
             'rootid': self._user2_project2.rootFolder.id}
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

        projectobj=Project.objects.get(author=self._user1,name=self._newname1)

        # Teste, dass der Server eine positive Antwort geschickt hat
        serveranswer = {'id': projectobj.id, 'name': self._newname1, 'rootid':projectobj.rootFolder.id}
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
        self.assertFalse(Folder.objects.filter(root=self._user1_project1.rootFolder,name='Ordner 1'))


        # Die Binärdatei sollte eine ILLEGALFILETYPE Fehlermeldung hervorrufen
        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['ILLEGALFILETYPE']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)


        # --------------------------------------------------------------------------------------------------------------
        # erstelle eine Datei mit zufälligem Inhalt (keine gültige zip Datei)
        zip_file_path = os.path.join(tmpfolder, (self._newname3 + '.zip'))
        zip_file = open(zip_file_path, 'a+b')
        zip_file.write(os.urandom(8))
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
        serveranswer = ERROR_MESSAGES['ILLEGALFILETYPE']

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
        serveranswer = ERROR_MESSAGES['ILLEGALFILETYPE']

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
        self.assertEqual(response['Content-Type'], mimetypes.types_map['.zip'])
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
        with open(tmp_zip_file, 'a+b') as f:
            f.write(response.content)

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
        with open(maintex_path, 'r') as maintex:
            self.assertEqual(maintex.read(), self._user1_tex1.source_code)

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
        with self._user1_binary1.getContent() as binfilecontent:
            tmp_binary1 = open(binary1_path, 'rb')
            self.assertEqual(tmp_binary1.read(), binfilecontent.read())
            tmp_binary1.close()

        # Lösche die temporäre zip Datei und das temp Verzeichnis
        if os.path.isdir(tmpfolder):
            shutil.rmtree(tmpfolder)

        # --------------------------------------------------------------------------------------------------------------
        # sende Anfrage zum exportieren eines Ordners
        response = util.documentPoster(self, command='exportzip', idpara=self._user1_project1_folder2.id)

        # überprüfe die Antwort des Servers
        # Content-Type sollte application/zip sein
        self.assertEqual(response['Content-Type'], mimetypes.types_map['.zip'])
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
        with open(tmp_zip_file, 'a+b') as f:
            f.write(response.content)

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
        with self._user1_binary1.getContent() as binfilecontent:
            tmp_binary1 = open(binary1_path, 'rb')
            self.assertEqual(tmp_binary1.read(), binfilecontent.read())
            tmp_binary1.close()

        # Lösche die temporäre zip Datei und das temp Verzeichnis
        if os.path.isdir(tmpfolder):
            shutil.rmtree(tmpfolder)

        # --------------------------------------------------------------------------------------------------------------
        # sende Anfrage zum exportieren eines Ordners mit einer ungültigen projectid
        response = util.documentPoster(self, command='exportzip', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)

        # --------------------------------------------------------------------------------------------------------------
        # sende Anfrage zum exportieren eines Projektes mit einer rootfolderID die user2 gehört (als user1)
        response = util.documentPoster(self, command='exportzip', idpara=self._user2_project1.rootFolder.id)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)

    def test_shareProject(self):
        """Test der shareProject() Methode des project view

        Teste die Freigabe eines Projektes für andere Benutzer.

        Testfälle:
        +++ Methode noch nicht implementiert +++

        :return: None
        """
        pass
