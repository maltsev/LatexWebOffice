"""

* Purpose : Test der Allgemeinen Links

* Creation Date : 25-11-2014

* Last Modified : Do 04 Dez 2014 15:23:33 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 2

* Backlog entry :

"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
import json
from app.tests.server.viewtestcase import ViewTestCase


class MainTestClass(ViewTestCase):
    # Initialiserung der benötigten Objekte
    # -> wird vor jedem Test ausgeführt
    def setUp(self):
        self.setUpSingleUser()


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass


    # Test der Impressum Seite
    def test_impressum(self):
        # Teste ob Impressum unter der URL aufrufbar ist und das richtige Template nutzt
        response = self.client.get('/impressum/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'impressum.html')


    # Test der Hilfe Seite
    def test_hilfe(self):
        # Teste ob Hilfe unter der URL aufrufbar ist und das richtige Template nutzt
        response = self.client.get('/hilfe/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hilfe.html')


    # Test der Editor Seite
    def test_editor(self):
        # Teste ob Editor unter der URL aufrufbar ist und das richtige Template nutzt
        response = self.client.get('/editor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editor.html')

        # Teste ob Editor zur login Seite weiterleitet, sofern kein Benutzer eingeloggt ist
        # logge user1 aus
        self.client.logout()
        response = self.client.get('/editor/')
        #redirect zur loginseite
        self.assertEqual(response.status_code, 302)