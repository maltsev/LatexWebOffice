# -*- coding: utf-8 -*-
"""

* Purpose : Vorlage Modell (app/models/projecttemplate.py)

* Creation Date : 10-12-2014

* Last Modified : 10 Dec 2014 13:17:00 CET

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




class ProjectTemplateManager(models.Manager):
    def createFromProject(self, **kwargs):
        if 'project' not in kwargs:
            raise AttributeError('Project ist nicht eingegeben')

        project = kwargs['project']

        projectTemplateName = kwargs.get('name', "{} (Vorlage)".format(project.name))
        projectTemplateAuthor = kwargs.get('author', project.author)

        projectTemplate = self.create(name=projectTemplateName, author=projectTemplateAuthor)

        Folder.objects.copy(project.rootFolder, projectTemplate.rootFolder)

        return projectTemplate


    def createFromProjectTemplate(self, **kwargs):
        raise NotImplementedError('createFromProjectTemplate soll von Project angerufen werden')


class ProjectTemplate(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    createTime = models.DateTimeField(auto_now_add=True)
    rootFolder = models.OneToOneField("Folder")
    objects = ProjectTemplateManager()

    class Meta:
        unique_together = ('name', 'author')

    def __str__(self):
        return "{}_{}".format(self.pk, self.name)


@receiver(post_delete, sender=ProjectTemplate)
def projectTemplatePostDelete(instance, **kwargs):
    if instance.rootFolder:
        instance.rootFolder.delete()

##
# Automatische Erzeugung des Rootverzeichnises
@receiver(pre_save, sender=ProjectTemplate)
def projectTemplatePreSave(instance, **kwargs):
    if not hasattr(instance, 'rootFolder') or not instance.rootFolder:
        randomFolderName = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
        rootFolder = Folder.objects.create(name=randomFolderName)
        instance.rootFolder = rootFolder
