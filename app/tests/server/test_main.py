"""

* Purpose : Test der Allgemeinen Links

* Creation Date : 25-11-2014

* Last Modified : Tue 25 Nov 2014 01:01:50 PM CET

* Author :  mattis

* Coauthors : 

* Sprintnumber : 2

* Backlog entry :

"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
import json


class MainTestClass(TestCase):
    # Initialiserung der benötigten Objekte
    # -> wird vor jedem Test ausgeführt
    def setUp(self):
        pass


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass


    # Teste ob Impressum unter der URL aufrufbar ist und das richtige Template nutzt
    def test_impressum(self):
        response = self.client.get('/impressum/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'impressum.html')


    # Teste ob Hilfe unter der URL aufrufbar ist und das richtige Template nutzt
    def test_hilfe(self):
        response = self.client.get('/hilfe/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hilfe.html')


    # Teste ob Editor unter der URL aufrufbar ist und das richtige Template nutzt
    def test_editor(self):
        response = self.client.get('/editor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editor.html')