# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.admin.models import User

from app.middleware import SingleSignOnMiddleware
import settings


class SingleSignOnMiddlewareTestClass(TestCase):

    def test_process_request(self):
        # Neue Benutzer
        response = self.client.get('/projekt/', REMOTE_USER='j_smit03', HTTP_X_TRUSTED_REMOTE_NAME='John&nbsp;Smith')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projekt.html')
        self.assertTrue(response.context['user'].is_authenticated())

        user = User.objects.get(username='j_smit03@uni-muenster.de')
        self.assertEqual(user.email, 'j_smit03@uni-muenster.de')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Smith')




        User.objects.create(username='p_adam01@uni-muenster.de', email='p_adam01@uni-muenster.de',
                            first_name='Paul', last_name='Adams')

        users_num = User.objects.count()

        # Bereits existierende Benutzer
        response = self.client.get('/vorlagen/', REMOTE_USER='p_adam01')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vorlagen.html')
        self.assertTrue(response.context['user'].is_authenticated())

        user = User.objects.get(username='p_adam01@uni-muenster.de')
        self.assertEqual(user.email, 'p_adam01@uni-muenster.de')
        self.assertEqual(user.first_name, 'Paul')
        self.assertEqual(user.last_name, 'Adams')

        self.assertEqual(User.objects.count(), users_num)




        settings.SSO_LOGOUT_URL = 'https://sso.uni-muenster.de/SingleSignOff'

        # Abmeldung
        response = self.client.get('/logout/', REMOTE_USER='p_adam01')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/login/')




    def test_split_name(self):
        obj = SingleSignOnMiddleware()

        self.assertEqual(obj.split_name('John&nbsp;Smith'), ('John', 'Smith'))
        self.assertEqual(obj.split_name('Cassio&nbsp;van&nbsp;den&nbsp;Berg'), ('Cassio van den Berg', ''))
        self.assertEqual(obj.split_name('Maria&nbsp;Rebekka&nbsp;Sch&auml;fer'), (u'Maria Rebekka Schäfer', ''))