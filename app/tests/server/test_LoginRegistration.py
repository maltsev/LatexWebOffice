""" 

* Purpose : Testing of essential registration and login functionality

* Creation Date : 06-11-2014

* Last Modified : Thu 13 Nov 2014 11:30:05 AM CET

* Author : mattis

* Coauthors : christian

* Sprintnumber : 1 
    
"""


from django.test import TestCase,Client
from django.contrib.auth.models import User
from core.settings import LOGIN_URL, ERROR_MESSAGES
from django.contrib.auth import login, authenticate

class LoginTestClass(TestCase):

    """Docstring for LoginTestClass. """

    # Setup method. It constructs two users and a client object to do requests with:
    # user1 - an active user
    # user2 - an inactive user
    # client - the client to do requests with
    def setUp(self):
        # create active user1
        user1 = User.objects.create_user(
            username='user1@test.de', password='123456')
        user1._unhashedpw = '123456'
        self._user1 = user1

        # create inactive user2
        user2 = User.objects.create_user(
            'user2@test.de', password='test123')
        user2._unhashedpw = 'test123'
        user2.is_active = False
        user2.save()
        self._user2 = user2

        self._client = Client()

    # Test if a user is not logged in with an incorrect password -> user1
    def test_loginFailIncorrectPassword(self):
        response = self._client.post(
            '/login/', {'email': self._user1.username, 'password': 'wrong'})
        self.assertNotIn('_auth_user_id', self._client.session)

    # Test if an user receives a failure message on incorrect login -> user1
    def test_loginFailIncorrectUsername(self):
        response = self._client.post(
            '/login/', {'email': 'wrongusername', 'password': self._user1._unhashedpw})
        self.assertContains(response, ERROR_MESSAGES['WRONGLOGINCREDENTIALS'])

    # Test if a user can't login when he is set inactive -> user2
    def test_loginFailInactiveUser(self):
        response = self._client.post(
            '/login/', {'email': self._user2.username, 'password': self._user2._unhashedpw})
        self.assertContains(response, ERROR_MESSAGES['INACTIVEACCOUNT'].format(self._user2.username))

    # Test if a user is logged in with an correct password -> user1
    def test_loginSuccess(self):
        response = self._client.post(
            '/login/', {'email': self._user1.username, 'password':self._user1._unhashedpw})
        self.assertIn('_auth_user_id', self._client.session)

    #Test that if an already logged in user tries to login, a redirect to the start page will be done
    def test_redirectForAuthenticatedUsers(self):
        self._client.login(username=self._user1.username,password=self._user1._unhashedpw)
        response=(self._client.get('/login/'))
        self.assertRedirects(response,'/')



    def test_logoutUser(self):
        self._client.login(username=self._user1.username,password=self._user1._unhashedpw)
        self.assertIn('_auth_user_id',self._client.session)
        response=self._client.get('/logout/')
        self.assertNotIn('_auth_user_id',self._client.session)
        self.assertRedirects(response,'/login/')




class RegistrationTestClass(TestCase):

    """Docstring for RegistrationTestClass. """

    # Setup method. It constructs 4 user data sets and a client object to do requests with:
    # user1 - should register and login successfully; second registration with same email should fail
    # user2 - incorrect email address, registration should fail
    # user3 - one blank field, registration should fail
    # user4 - different password, registration should fail
    # user 5 - password contains spaces, registration should fail
    # client - the client to do requests with
    def setUp(self):

        # user 1 data -> everything correct
        self._user1_first_name = 'user1'
        self._user1_email = 'user1@test.de'
        self._user1_password1 = 'test123'
        self._user1_password2 = 'test123'

        # user 2 data -> incorrect email address (username)
        self._user2_first_name = 'user2'
        self._user2_email = 'user2@test'
        self._user2_password1 = 'test1234'
        self._user2_password2 = 'test1234'

        # user 3 data -> contains a blank field
        self._user3_first_name = ''
        self._user3_email = 'user3@test.de'
        self._user3_password1 = 'test'
        self._user3_password2 = 'test'

        # user 4 data -> passwords do not match
        self._user4_first_name = 'user4'
        self._user4_email = 'user4@test.de'
        self._user4_password1 = 'test123'
        self._user4_password2 = 'test12'

        # user 5 data -> password contains spaces
        self._user5_first_name = 'user5'
        self._user5_email = 'user5@test.de'
        self._user5_password1 = 'test 123'
        self._user5_password2 = 'test 123'

        # user 6 data -> first_name contains illegal character
        self._user6_first_name = 'user6©'
        self._user6_email = 'user6@test.de'
        self._user6_password1 = 'test123'
        self._user6_password2 = 'test123'

        self._client = Client()

    # Test if you successfully register when you fill out all fields and
    # enter a valid email address -> user1
    # if automatic login after registration was successful this test passes
    def test_registrationSuccess(self):
        response = self._client.post(
            '/registration/', {'first_name': self._user1_first_name, 'email': self._user1_email,
            'password1': self._user1_password1, 'password2': self._user1_password2})
        self.assertIn('_auth_user_id', self._client.session)

    # Test if you can't register when same email is already registered
    def test_registrationFailAlreadyRegistered(self):
        # create user1 separately again, because user1 from first registrationSuccess
        # doesn't exist here in our database
        new_user = User.objects.create_user(username=self._user1_email,
                                               email=self._user1_email, password=self._user1_password1,
                                               first_name=self._user1_first_name)
        response = self._client.post(
            '/registration/', {'first_name': self._user1_first_name, 'email': self._user1_email,
            'password1': self._user1_password1, 'password2': self._user1_password2}, follow=True)
        self.assertContains(response, ERROR_MESSAGES['EMAILALREADYEXISTS'])

    # Test if you can't register with an invalid email address -> user 2
    def test_registrationFailInvalidEmail(self):
        response = self._client.post(
            '/registration/', {'first_name': self._user2_first_name, 'email': self._user2_email,
            'password1': self._user2_password1, 'password2': self._user2_password2})
        self.assertContains(response, ERROR_MESSAGES['INVALIDEMAIL'])

    # Test if you can't register when you didn't fill out all fields -> user3
    def test_registrationFailNotFilledAllFields(self):
        response = self._client.post(
            '/registration/', {'first_name': self._user3_first_name, 'email': self._user3_email,
            'password1': self._user3_password1, 'password2': self._user3_password2})
        self.assertContains(response, ERROR_MESSAGES['NOEMPTYFIELDS'])

    # Test if you can't register when the passwords do not match -> user4
    def test_registrationFailPasswordsDontMatch(self):
        response = self._client.post(
            '/registration/', {'first_name': self._user4_first_name, 'email': self._user4_email,
            'password1': self._user4_password1, 'password2': self._user4_password2})
        self.assertContains(response, ERROR_MESSAGES['PASSWORDSDONTMATCH'])

    # Test if you can't register when password contains spaces -> user5
    def test_registrationFailPasswordContainsSpaces(self):
        response = self._client.post(
            '/registration/', {'first_name': self._user5_first_name, 'email': self._user5_email,
            'password1': self._user5_password1, 'password2': self._user5_password2})
        self.assertContains(response, ERROR_MESSAGES['NOSPACESINPASSWORDS'])

    # Test if you can't register when first_name contains illegal characters
    def test_registrationFailFirstNameIllegalChar(self):
        response = self._client.post(
            '/registration/', {'first_name': self._user6_first_name, 'email': self._user6_email,
            'password1': self._user6_password1, 'password2': self._user6_password2})
        self.assertContains(response, ERROR_MESSAGES['INVALIDCHARACTERINFIRSTNAME'])
