# -*- coding: utf-8 -*-
"""

* Purpose : Projekt Modell (app/models/project.py)

* Creation Date : 20-11-2014

* Last Modified : 4 Dec 2014 13:17:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from app.models.folder import Folder




class ProjectManager(models.Manager):
    def createFromProject(self, **kwargs):
        pass


    def createFromProjectTemplate(self, **kwargs):
        pass



class Project(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    createTime = models.DateTimeField(auto_now_add=True)
    rootFolder = models.ForeignKey(Folder)
    objects = ProjectManager()

    class Meta:
        unique_together = ('name', 'author')

    def __str__(self):
        return "{}_{}".format(self.pk, self.name)


@receiver(post_delete, sender=Project)
def projectPostDelete(instance, **kwargs):
    instance.rootFolder.delete()

##
# Automatische Erzeugung des Rootverzeichnises
@receiver(pre_save, sender=Project)
def projectPreSave(instance, **kwargs):
    if not hasattr(instance, 'rootFolder') or not instance.rootFolder:
        randomFolderName = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
        rootFolder = Folder.objects.create(name=randomFolderName)
        instance.rootFolder = rootFolder
