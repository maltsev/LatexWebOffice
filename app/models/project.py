# -*- coding: utf-8 -*-
"""

* Purpose : Projekt Modell (app/models/project.py)

* Creation Date : 20-11-2014

* Last Modified : 10 Dec 2014 13:17:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from app.models import projecttemplate, folder


class ProjectManager(models.Manager):
    def createFromProject(self, **kwargs):
        raise NotImplementedError('createFromProject soll von ProjectTemplate angerufen werden')

    def createFromProjectTemplate(self, **kwargs):
        if 'template' not in kwargs:
            raise AttributeError('ProjectTemplate ist nicht eingegeben')

        projectTemplate = kwargs['template']

        projectName = kwargs.get('name', projectTemplate.name)
        projectAuthor = kwargs.get('author', projectTemplate.author)

        project = self.create(name=projectName, author=projectAuthor)

        folder.Folder.objects.copy(projectTemplate.rootFolder, project.rootFolder)

        return project


class Project(projecttemplate.ProjectTemplate):
    objects = ProjectManager()


##
# Automatische Erzeugung des Rootverzeichnises
@receiver(pre_save, sender=Project)
def projectPreSave(instance, **kwargs):
    projecttemplate.projectTemplatePreSave(instance, **kwargs)
