"""

* Purpose : Test des Oroject Views und zugehöriger Methoden (app/views/project.py)

* Creation Date : 26-11-2014

* Last Modified : Do 04 Dez 2014 10:50:19 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : -

"""


from app.common.constants import ERROR_MESSAGES, SUCCESS
from app.common import util
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.plaintextfile import PlainTextFile
from app.tests.server.viewtestcase import ViewTestCase
import tempfile
import zipfile
import shutil
import os
import mimetypes


class ProjectTestClass(ViewTestCase):

    # Initialiserung der benötigten Objekte
    # -> wird vor jedem Test ausgeführt

    def setUp(self):
        self.setUpUserAndProjects()
        self.setUpFolders()
        self.setUpValues()

    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass

    # Teste Erstellen eines Projektes:
    # - ein Benutzer erstellt zwei neue Projekte -> success
    # - ein Benutzer erstellt ein weiteres Projekt, wobei der Projektname nur aus Leerzeichen besteht -> Fehlermeldung
    # - ein Benutzer erstellt ein weiteres Projekt, wobei der Projektname bereits existiert -> Fehlermeldung
    def test_projectCreate(self):
        # Sende Anfrage zum Erstellen eines neuen Projektes
        response = util.documentPoster(
            self, command='projectcreate', name=self._newprojectname2)

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)
        # teste ob id vorhanden ist
        self.assertIn('id', dictionary['response'])
        # teste ob name vorhanden ist
        self.assertIn('name', dictionary['response'])
        # teste ob name mit dem übergebenen Projektnamen übereinstimmt
        self.assertEqual(dictionary['response']['name'], self._newprojectname2)

        # id vom Projekt 3 von user1
        user1_project3_id = dictionary['response']['id']

        # erzeuge ein weiteres Projekt
        response = util.documentPoster(
            self, command='projectcreate', name=self._newprojectname3)

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # id vom Projekt 4 von user1
        user1_project4_id = dictionary['response']['id']

        # überprüfe, ob die erstellten Projekte in der Datenbank vorhanden sind
        # user1_project3
        self.assertTrue(Project.objects.get(id=user1_project3_id))
        # user1_project4
        self.assertTrue(Project.objects.get(id=user1_project4_id))
        # überprüfe ob für diese Projekte der root Ordner in der Datenbank
        # angelegt wurde
        self.assertTrue(Project.objects.get(id=user1_project3_id).rootFolder)
        self.assertTrue(Project.objects.get(id=user1_project4_id).rootFolder)

        # überprüfe, ob die main.tex Dateien in der Datenbank vorhanden sind
        self.assertTrue(
            Project.objects.get(id=user1_project3_id).rootFolder.getMainTex())
        self.assertTrue(
            Project.objects.get(id=user1_project4_id).rootFolder.getMainTex())

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name nur aus Leerzeichen besteht
        response = util.documentPoster(
            self, command='projectcreate', name='    ')

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # Fehlermeldung sollte ERROR_MESSAGES['BLANKNAME'] sein
        util.validateJsonFailureResponse(
            self, response.content, ERROR_MESSAGES['BLANKNAME'])

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name ungültige Sonderzeichen enthält
        response = util.documentPoster(
            self, command='projectcreate', name='<>\\')

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # status sollte failure sein
        # Fehlermeldung sollte ERROR_MESSAGES['INVALIDNAME'] sein
        util.validateJsonFailureResponse(
            self, response.content, ERROR_MESSAGES['INVALIDNAME'])

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein weiteres Projekt mit einem bereits existierenden Namen
        response = util.documentPoster(
            self, command='projectcreate', name='USER1_project4')

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # Fehlermeldung sollte ERROR_MESSAGES['PROJECTALREADYEXISTS'] sein
        util.validateJsonFailureResponse(self, response.content,
                                         ERROR_MESSAGES['PROJECTALREADYEXISTS'].format('USER1_project4'))

    # Teste Löschen eines Projektes
    def test_projectRm(self):
        # Sende Anfrage zum Löschen eines vorhandenen Projektes
        response = util.documentPoster(
            self, command='projectrm', idpara=self._user1_project1.id)

        # überprüfe die Antwort des Servers
        # status sollte success sein
        util.validateJsonSuccessResponse(self, response.content, {})

        # es sollte keine Ordner des Projektes mehr in der Datenbank existieren
        self.assertFalse(
            Folder.objects.filter(id=self._user1_project1_folder1.id))
        self.assertFalse(
            Folder.objects.filter(id=self._user1_project1_folder2_subfolder1.id))

        # Sende Anfrage zum Löschen eines nicht vorhandenen Projektes
        response = util.documentPoster(
            self, command='projectrm', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # Fehlermeldung sollte ERROR_MESSAGES['PROJECTNOTEXIST'] sein
        util.validateJsonFailureResponse(
            self, response.content, ERROR_MESSAGES['PROJECTNOTEXIST'])

        # Sende Anfrage zum Löschen eines Projektes von user2 (als user1)
        response = util.documentPoster(
            self, command='projectrm', idpara=self._user2_project1.id)

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # Fehlermeldung sollte ERROR_MESSAGES['NOTENOUGHRIGHTS'] sein
        util.validateJsonFailureResponse(
            self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

    # Teste Auflisten aller Projekte:
    # - user1 und user2 besitzen jeweils 2 Projekte, user3 keine
    # - user1 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user2 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user3 bekommt keine Projekte aufgelistet
    def test_listprojects(self):
        # Sende Anfrage zum Auflisten aller Projekte von user1
        response = util.documentPoster(self, command='listprojects')

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # teste, ob in response die beiden erstellten Projekte von user1 richtig aufgelistet werden
        # und keine Projekte von user2 aufgelistet werden
        dictionary = [{'id': self._user1_project1.id, 'name': self._user1_project1.name},
                      {'id': self._user1_project2.id, 'name': self._user1_project2.name}]
        util.validateJsonSuccessResponse(self, response.content, dictionary)

        # logout von user1
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user2
        self.client.login(
            username=self._user2.username, password=self._user2._unhashedpw)

        # Sende Anfrage zum Auflisten aller Projekte von user2
        response = util.documentPoster(self, command='listprojects')

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # teste, ob in response die beiden erstellten Projekte von user 2 richtig aufgelistet werden
        # und keine Projekte von user1 aufgelistet werden
        dictionary = [{'id': self._user2_project1.id, 'name': self._user2_project1.name},
                      {'id': self._user2_project2.id, 'name': self._user2_project2.name}]
        util.validateJsonSuccessResponse(self, response.content, dictionary)

        # logout von user2
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user3
        self.client.login(
            username=self._user3.username, password=self._user3._unhashedpw)

        # Sende Anfrage zum Auflisten aller Projekte von user3
        response = util.documentPoster(self, command='listprojects')

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # response sollte [] sein
        util.validateJsonSuccessResponse(self, response.content, [])

    # Teste das Importieren von Projekten mit einer .zip Datei
    def test_importzip(self):
        # erstelle ein temp Verzeichnis
        tmpfolder = tempfile.mkdtemp()

        # erstelle im temp Verzeichnis einen Projektordner und einige
        # Unterordner
        tmpfolder_project = os.path.join(tmpfolder, self._newprojectname1)
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

        # erstelle eine Binärdatei im Unterordner 1
        binfile = open(os.path.join(
            tmpfolder_project, 'Ordner 1', 'Unterordner 1', 'binary1.bin'), 'wb')
        binfile.write(bytearray('binary_test_file_importzip', 'utf-8'))
        binfile.close()

        # erstelle eine zip Datei aus dem Projektordner
        zip_file_path = os.path.join(
            tmpfolder, (self._newprojectname1 + '.zip'))
        util.createZipFromFolder(tmpfolder_project, zip_file_path)

        # stelle sicher, dass die zip Datei gültig ist
        self.assertTrue(zipfile.is_zipfile(zip_file_path))

        # lese die zip Datei ein und schreibe die Daten in den request
        zip = open(zip_file_path, 'rb')
        request = {
            'command': 'importzip',
            'files': [zip]
        }

        self.client.post('/documents/', request)
        zip.close()

        # Lösche alle erstellten temporären Dateien und Verzeichnisse
        if os.path.isdir(tmpfolder):
            shutil.rmtree(tmpfolder)

        # Teste, dass das Projekt existiert
        self.assertTrue(Project.objects.filter(
            author=self._user1, name=self._newprojectname1).exists())
        projobj = Project.objects.get(
            author=self._user1, name=self._newprojectname1)

        # Teste, dass eine main tex Datei existiert und diese den richtigen
        # Inhalt hat
        self.assertTrue(PlainTextFile.objects.filter(
            name='main.tex', folder=projobj.rootFolder).exists())
        maintexobj = PlainTextFile.objects.get(
            name='main.tex', folder=projobj.rootFolder)
        self.assertEqual(maintexobj.source_code, self._new_code1)

        # Teste, dass auch Unterordner angelegt wurden
        self.assertTrue(
            Folder.objects.filter(name='Unterordner 1', root=projobj.rootFolder).exists())

    # Teste das Exportieren eines Projektes als .zip Datei
    def test_exportzip(self):
        # lese die main.tex Datei von user1_project1 ein und setze einen test
        # String als source_code
        maintexobj = self._user1_project1.rootFolder.getMainTex()
        maintexobj.source_code = 'test_sourcecode for exportzip'
        maintexobj.save()

        # Sende Anfrag zum exportieren eines Projektes
        response = util.documentPoster(
            self, command='exportzip', idpara=self._user1_project1.id)

        # überprüfe die Antwort des Servers
        # Content-Type sollte application/zip sein
        self.assertEqual(response['Content-Type'], mimetypes.types_map['.zip'])
        # Content-Length sollte mit gesendet worden sein
        self.assertIn('Content-Length', response)

        # erstelle temp Ordner
        tmpfolder = tempfile.mkdtemp()
        tmpfolder_extracted = os.path.join(tmpfolder, 'extracted')
        if not os.path.isdir(tmpfolder_extracted):
            os.mkdir(tmpfolder_extracted)

        # Pfad zur temporären zip Datei
        tmp_zip_file = os.path.join(
            tmpfolder, (self._user1_project1.name + 'zip'))
        # Schreibe den Inhalt der empfangenen Datei in die temp zip Datei
        with open(tmp_zip_file, 'a+b') as f:
            f.write(response.content)

        # überprüfe, ob es eine gültige zip Datei ist (magic number)
        self.assertTrue(zipfile.is_zipfile(tmp_zip_file))

        # entpacke die heruntergeladene Datei
        util.extractZipToFolder(tmpfolder_extracted, tmp_zip_file)

        # überprüfe ob der folder1 vorhanden ist
        self.assertTrue(os.path.isdir(
            os.path.join(tmpfolder_extracted, self._user1_project1_folder1.name)))
        # überprüfe ob der folder2_subfolder1 vorhanden ist
        self.assertTrue(os.path.isdir(os.path.join(tmpfolder_extracted, self._user1_project1_folder2.name,
                                                   self._user1_project1_folder2_subfolder1.name)))
        # überprüfe ob die main.tex Datei vorhanden ist
        maintex_path = os.path.join(tmpfolder_extracted, maintexobj.name)
        self.assertTrue(os.path.isfile(maintex_path))

        # überprüfe, ob der Inhalt der main.tex Datei mit der Datenbank
        # übereinstimmt
        with open(maintex_path, 'r') as maintex:
            self.assertEqual(maintex.read(), maintexobj.source_code)

        # Lösche die temporäre zip Datei und das temp Verzeichnis
        # if os.path.isdir(tmpfolder):
        #    shutil.rmtree(tmpfolder)

        # sende Anfrage zum exportieren eines Projektes mit einer ungültigen
        # projectid
        response = util.documentPoster(
            self, command='exportzip', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)

        # sende Anfrage zum exportieren eines Projektes mit einer projectid,
        # die user2 gehört (als user1)
        response = util.documentPoster(
            self, command='exportzip', idpara=self._user2_project1.id)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)

    # Teste die Freigabe eines Projektes für andere Benutzer
    def test_shareproject(self):
        pass
