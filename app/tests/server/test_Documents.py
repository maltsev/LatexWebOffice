"""

* Purpose : Test der Dokument- und Projektverwaltung (app/view/documents.py)

* Creation Date : 20-11-2014

* Last Modified : Do 20 Nov 2014 14:33:53 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry :

"""

from django.test import TestCase,Client
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common.util import jsonDecoder
from app.models.project import Project
from app.models.folder import Folder
from app.models.file.document import Document


class LoginTestClass(TestCase):
    def setUp(self):

        # erstelle user1
        self._user1 = User.objects.create_user(
            username='user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'

        # erstelle user2
        self._user2 = User.objects.create_user(
            'user2@test.de', password='test123')
        self._user2._unhashedpw = 'test123'

        # erstelle user3
        self._user3 = User.objects.create_user(
            'user3@test.de', password='test1234')
        self._user3._unhashedpw = 'test1234'

    def tearDown(self):
        self.client.logout()

    # Teste Erstellen eines Projektes:
    # - ein Benutzer erstellt zwei neue Projekte -> success
    # - ein Benutzer erstellt ein weiteres Projekt, wobei der Projektname nur aus Leerzeichen besteht -> Fehlermeldung
    # - ein Benutzer erstellt ein weiteres Projekt, wobei der Projektname bereits existiert -> Fehlermeldung
    def test_projectCreate(self):

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Erstellen eines Projektes auf
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project1'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)
        # teste ob id vorhanden ist
        self.assertIn('id', dictionary['response'])
        # teste ob name vorhanden ist
        self.assertIn('name', dictionary['response'])
        # teste ob name mit dem übergebenen Projektnamen übereinstimmt
        self.assertEqual(dictionary['response']['name'], 'user1_project1')

        # erzeuge ein weiteres Projekt
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project2'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name nur aus Leerzeichen besteht
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': '    '})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['PROJECTNAMEONLYWHITESPACE'])

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein weiteres Projekt mit einem bereits existierenden Namen
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project2'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['PROJECTALREADYEXISTS'].format('user1_project2'))


    # Teste Auflisten aller Projekte:
    # - user1 und user2 besitzen jeweils 2 Projekte, user3 keine
    # - user1 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user2 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user3 bekommt keine Projekte aufgelistet
    def test_listprojects(self):

        # erstelle zwei Projekte als user1
        user1_project1 = Project.objects.create(name='user1_project1', author=self._user1)
        user1_project1.save()
        user1_project2 = Project.objects.create(name='user1_project2', author=self._user1)
        user1_project2.save()

        # erstelle zwei Projekte als user2
        user2_project1 = Project.objects.create(name='user2_project1', author=self._user2)
        user2_project1.save()
        user2_project2 = Project.objects.create(name='user2_project2', author=self._user2)
        user2_project2.save()

        # login von user1
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response die beiden erstellten Projekte von user1 richtig aufgelistet werden
        # und keine Projekte von user2 aufgelistet werden
        self.assertEqual(dictionary['response'],
                         [{'id': user1_project1.id, 'name': user1_project1.name},
                         {'id': user1_project2.id, 'name': user1_project2.name}])

        # logout von user1
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response die beiden erstellten Projekte von user 2 richtig aufgelistet werden
        # und keine Projekte von user1 aufgelistet werden
        self.assertEqual(dictionary['response'],
                         [{'id': user2_project1.id, 'name': user2_project1.name},
                         {'id': user2_project2.id, 'name': user2_project2.name}])

        # logout von user2
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user3
        self.client.login(username=self._user3.username, password=self._user3._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response ein leeres Array übergeben wurde, da user3 keine Projekte besitzt
        self.assertEqual(dictionary['response'], [])