""" 

* Purpose :

* Creation Date : 06-11-2014

* Last Modified : Thu 06 Nov 2014 07:20:54 PM CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 1 
    
"""


from django.test import TestCase,Client
from django.contrib.auth.models import User


class LoginTestClass(TestCase):

    """Docstring for LoginTestClass. """

# Setup method. It constructs two users and a Client object to do requests with:
# user1active - an active user
# user2inactive - an inactive user
# client - the client to do requests with

    def setUp(self):
        user1active = User.objects.create_user(
            'test@test.com', password='123456')
        user1active.save()
        self._user1active = user1active
        user2inactive = User.objects.create_user(
            'test2@test.com', password='none')
        user2inactive.is_active = False
        user2inactive.save()
        self._user2inactive = user2inactive
        self._client = Client()
# Tests if on incorrect login the client received a failure message and is
# directed to the login page

    def test_loginFails(self):
        # Testing that a user is not logged in with an incorrect password
        response = self._client.post(
            '/login/', {'email': self._user1active.username, 'password': 'wrong'})
        self.assertNotIn('_auth_user_id', self.client.session)

        # Testing that an user receives a failure message on incorrect login

        # Testing that an user is directed to the login page again

    def test_loginSuccess(self):

        # Testing that a user is logged in with an correct password

        # Testing that a user is directed tothe "Startseite" after an correct
        # password

        pass



class RegistrationTestClass(TestCase):

    """Docstring for RegistrationTestClass. """

    def setUp(self):
        self._client = Client()

# Tests that you successfully register when you fill out all fields and
# enter a valid email address
    def test_registerSuccess(self):
        pass

# Tests that you can't register with an invalid email address
    def test_loginFalseInvalidEmail(self):
        pass

# Tests that you can't register when you didn't fill out all fields
    def test_loginFalseNotFilledAllFields(self):
        pass









