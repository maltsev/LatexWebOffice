"""

* Purpose : Test der Allgemeinen Links

* Creation Date : 25-11-2014

* Last Modified : Tue 25 Nov 2014 01:01:50 PM CET

* Author :  mattis

* Coauthors : 

* Sprintnumber : 2

* Backlog entry :

"""

from django.test import TestCase,Client
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
import json

class DocumementsTestClass(TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        self.client.logout()


    def test_impressum(self):
        response=self.client.get('/impressum/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'impressum.html')

    def test_hilfe(self):
        response=self.client.get('/hilfe/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'hilfe.html')

    def test_editor(self):
        response=self.client.get('/editor/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'editor.html')
