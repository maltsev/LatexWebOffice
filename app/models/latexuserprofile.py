""" 

* Purpose :

* Creation Date : 26-02-2015

* Last Modified : Do 26 Feb 2015 14:49:02 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 6

* Backlog entry : 

"""

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.db import models


class LatexUserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None):
        """
        Creates and saves a User with the given email, first_name and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            first_name=first_name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class LatexWebUser(AbstractBaseUser):
    first_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(verbose_name='email address',
        max_length=255,
        unique=True)

    first_name= models.CharField(max_length=30, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = LatexUserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def username(self):
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


