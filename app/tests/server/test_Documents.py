""" 

* Purpose :

* Creation Date : 20-11-2014

* Last Modified : Do 20 Nov 2014 14:33:53 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 2

* Backlog entry : 

"""

from django.test import TestCase,Client
from django.contrib.auth.models import User
from core.settings import LOGIN_URL, ERROR_MESSAGES
import json




class LoginTestClass(TestCase):
    def setUp(self):
        self._client=Client()

        response = self._client.post(
            '/registration/', {'first_name': 'test', 'email': 'test@test.de',
            'password1': '1234', 'password2': '1234'})


    def test_projectCreate(self):
        client=self._client
        response=client.post('/documents/',{'command': 'projectcreate', 'name':'myProject','testpara':123})
        print(response.content)
