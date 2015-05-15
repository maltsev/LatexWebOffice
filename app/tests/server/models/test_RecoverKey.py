import os
import datetime
import time

from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from app.models.recoverkey import RecoverKey


class RecoverKeyTestCase(TestCase):

    def test_getByUser(self):
        user = User.objects.create(username='test@test.com', email='test@test.com')
        recoverKey = RecoverKey.objects.getByUser(user)

        delta = recoverKey.expireTime - (datetime.datetime.now() + datetime.timedelta(days=1))
        self.assertTrue(delta < datetime.timedelta(seconds=1))
        self.assertTrue(RecoverKey.objects.isValid(user, recoverKey.key))
        self.assertEqual(RecoverKey.objects.count(), 1)

        recoverKey.expireTime = datetime.datetime.now() - datetime.timedelta(seconds=1)
        recoverKey.save()
        self.assertFalse(RecoverKey.objects.isValid(user, recoverKey.key))