"""

* Purpose : Test des Oroject Views und zugehöriger Methoden (app/views/project.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 26 Nov 2014 14:58:13 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : -

"""


from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common import util
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.tests.server.viewtestcase import ViewTestCase


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
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project3'})

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
        self.assertEqual(dictionary['response']['name'], 'user1_project3')

        # id vom Projekt 3 von user1
        user1_project3_id = dictionary['response']['id']

        # erzeuge ein weiteres Projekt
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project4'})

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
        # überprüfe ob für diese Projekte der root Ordner in der Datenbank angelegt wurde
        self.assertTrue(Project.objects.get(id=user1_project3_id).rootFolder)
        self.assertTrue(Project.objects.get(id=user1_project4_id).rootFolder)

        # überprüfe, ob die main.tex Dateien in der Datenbank vorhanden sind
        self.assertTrue(Project.objects.get(id=user1_project3_id).rootFolder.getMainTex())
        self.assertTrue(Project.objects.get(id=user1_project4_id).rootFolder.getMainTex())

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name nur aus Leerzeichen besteht
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': '    '})

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['BLANKNAME'])

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name ungültige Sonderzeichen enthält
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': '<>\\'})

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['INVALIDNAME'])

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein weiteres Projekt mit einem bereits existierenden Namen
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project4'})

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['PROJECTALREADYEXISTS'].format('user1_project4'))


    # Teste Löschen eines Projektes
    def test_projectRm(self):
        # Sende Anfrage zum Löschen eines vorhandenen Projektes
        response = util.documentPoster(self, command='projectrm', idpara=self._user1_project1.id)

        # überprüfe die Antwort des Servers
        # status sollte success sein
        util.validateJsonSuccessResponse(self, response.content, {})

        # es sollte keine Ordner des Projektes mehr in der Datenbank existieren
        self.assertFalse(Folder.objects.filter(id=self._user1_project1_folder1.id))
        self.assertFalse(Folder.objects.filter(id=self._user1_project1_folder2_subfolder1.id))

        # Sende Anfrage zum Löschen eines nicht vorhandenen Projektes
        response = util.documentPoster(self, command='projectrm', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['PROJECTNOTEXIST'])

        # Sende Anfrage zum Löschen eines Projektes von user2 (als user1)
        response = util.documentPoster(self, command='projectrm', idpara=self._user2_project1.id)

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])


    # Teste Auflisten aller Projekte:
    # - user1 und user2 besitzen jeweils 2 Projekte, user3 keine
    # - user1 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user2 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user3 bekommt keine Projekte aufgelistet
    def test_listprojects(self):
        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response die beiden erstellten Projekte von user1 richtig aufgelistet werden
        # und keine Projekte von user2 aufgelistet werden
        self.assertEqual(dictionary['response'],
                         [{'id': self._user1_project1.id, 'name': self._user1_project1.name},
                         {'id': self._user1_project2.id, 'name': self._user1_project2.name}])

        # logout von user1
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response die beiden erstellten Projekte von user 2 richtig aufgelistet werden
        # und keine Projekte von user1 aufgelistet werden
        self.assertEqual(dictionary['response'],
                         [{'id': self._user2_project1.id, 'name': self._user2_project1.name},
                         {'id': self._user2_project2.id, 'name': self._user2_project2.name}])

        # logout von user2
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user3
        self.client.login(username=self._user3.username, password=self._user3._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response ein leeres Array übergeben wurde, da user3 keine Projekte besitzt
        self.assertEqual(dictionary['response'], [])


    # Teste das Importieren von Projekten mit einer .zip Datei
    def test_importzip(self):
        pass


    # Teste das Exportieren eines Projektes als .zip Datei
    def test_exportzip(self):
        pass


    # Teste die Freigabe eines Projektes für andere Benutzer
    def test_shareproject(self):
        pass