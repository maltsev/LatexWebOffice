# -*- coding: utf-8 -*-
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from app.models.folder import Folder


class Project(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    createTime = models.DateTimeField(auto_now_add=True)
    rootFolder = models.ForeignKey(Folder)

    class Meta:
        unique_together = ('name', 'author')

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Project)
def projectPostDelete(instance, **kwargs):
    instance.rootFolder.delete()


@receiver(pre_save, sender=Project)
def projectPreSave(instance, **kwargs):
    if not hasattr(instance, 'rootFolder') or not instance.rootFolder:
        randomFolderName = ''.join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
        rootFolder = Folder.objects.create(name=randomFolderName)
        instance.rootFolder = rootFolder
