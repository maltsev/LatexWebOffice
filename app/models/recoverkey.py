import random
import string
import datetime

from django.db import models
from django.contrib.auth.models import User


class RecoverKeyManager(models.Manager):

    def getByUser(self, user):
        recoverKey = None
        try:
            recoverKey = self.get(user=user)
            if recoverKey.isExpired():
                recoverKey.delete()
                recoverKey = None

        except models.ObjectDoesNotExist:
            pass


        if not recoverKey:
            expireTime = datetime.datetime.now() + datetime.timedelta(days=1)
            recoverKey = self.create(key=self.generateKey(), expireTime=expireTime, user=user)


        return recoverKey


    def isValid(self, user, key):
        try:
            recoverKey = self.get(key=key)
            return not recoverKey.isExpired() and recoverKey.key == key
        except:
            return False


    def generateKey(self):
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))



class RecoverKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    expireTime = models.DateTimeField()
    user = models.ForeignKey(User, unique=True)
    objects = RecoverKeyManager()

    class Meta:
        app_label = 'app'


    def isExpired(self):
        return self.expireTime <= datetime.datetime.now()