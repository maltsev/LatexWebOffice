""" 

* Purpose : Testing of essential registration and login functionality

* Creation Date : 06-11-2014

* Last Modified : Thu 06 Nov 2014 07:20:54 PM CET

* Author : mattis

* Coauthors : christian

* Sprintnumber : 1 
    
"""


from django.test import TestCase,Client
from django.contrib.auth.models import User

class LoginTestClass(TestCase):

    """Docstring for LoginTestClass. """

    # Setup method. It constructs two users and a client object to do requests with:
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
        self.assertNotIn('_auth_user_id', self._client.session)

        # Testing that an user receives a failure message on incorrect login

        # Testing that an user is directed to the login page again

    def test_loginSuccess(self):

        # Testing that a user is logged in with an correct password

        # Testing that a user is directed to the "Startseite" after an correct
        # password

        pass



class RegistrationTestClass(TestCase):

    """Docstring for RegistrationTestClass. """

    # Setup method. It constructs 4 user data sets and a client object to do requests with:
    # user1 - should register and login successfully; second registration with same email should fail
    # user2 - incorrect email address, registration should fail
    # user3 - one blank field, registration should fail
    # user4 - different password, registration should fail
    #  client - the client to do requests with
    def setUp(self):

        # user 1 data -> everything correct
        self.user1_first_name = 'user1'
        self.user1_email = 'user1@test.de'
        self.user1_password1 = 'test123'
        self.user1_password2 = 'test123'

        # user 2 data -> incorrect email address (username)
        self.user2_first_name = 'user2'
        self.user2_email = 'user2@test'
        self.user2_password1 = 'test1234'
        self.user2_password2 = 'test1234'

        # user 3 data -> contains a blank field
        self.user3_first_name = ''
        self.user3_email = 'user3@test.de'
        self.user3_password1 = 'test'
        self.user3_password2 = 'test'

        # user 4 data -> passwords do not match
        self.user4_first_name = 'user4'
        self.user4_email = 'user3@test.de'
        self.user4_password1 = 'test123'
        self.user4_password2 = 'test12'

        self._client = Client()

    # Test if you successfully register when you fill out all fields and
    # enter a valid email address -> user1
    # if automatic login after registration was successful this test passes
    def test_registrationSuccess(self):
        response = self._client.post(
            '/registration/', {'first_name': self.user1_first_name, 'email': self.user1_email,
            'password1': self.user1_password1, 'password2': self.user1_password2})
        self.assertIn('_auth_user_id', self._client.session)

    # Test if you can't register when same email is already registered
    def test_registrationFailedAlreadyRegistered(self):
        # create user1 separately again, because user1 from first registrationSuccess
        # doesn't exist here in our database
        new_user = User.objects.create_user(username=self.user1_email,
                                               email=self.user1_email, password=self.user1_password1,
                                               first_name=self.user1_first_name)
        response = self._client.post(
            '/registration/', {'first_name': self.user1_first_name, 'email': self.user1_email,
            'password1': self.user1_password1, 'password2': self.user1_password2}, follow=True)
        self.assertContains(response, 'E-Mail-Adresse ist bereits registriert.')

    # Test if you can't register with an invalid email address -> user 2
    def test_registrationFailedInvalidEmail(self):
        response = self._client.post(
            '/registration/', {'first_name': self.user2_first_name, 'email': self.user2_email,
            'password1': self.user2_password1, 'password2': self.user2_password2})
        self.assertContains(response, 'Ungültige E-Mail-Adresse')

    # Test if you can't register when you didn't fill out all fields -> user3
    def test_registrationFailedNotFilledAllFields(self):
        response = self._client.post(
            '/registration/', {'first_name': self.user3_first_name, 'email': self.user3_email,
            'password1': self.user3_password1, 'password2': self.user3_password2})
        self.assertContains(response, 'Keine leeren Eingaben erlaubt.')

    # Test if you can't register when the passwords do not match
    def test_registrationFailedPasswordsDontMatch(self):
        response = self._client.post(
            '/registration/', {'first_name': self.user4_first_name, 'email': self.user4_email,
            'password1': self.user4_password1, 'password2': self.user4_password2})
        self.assertContains(response, 'Passwörter stimmen nicht überein.')