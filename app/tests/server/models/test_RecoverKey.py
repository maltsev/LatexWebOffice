import os
import datetime
import time

from django.test import TestCase

from app.models.recoverkey import RecoverKey
from app.common.util import getUserModel
User = getUserModel()


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