# -*- coding: utf-8 -*-
"""

* Purpose : Projekt Modell (app/models/project.py)

* Creation Date : 20-11-2014

* Last Modified : Do 26 Feb 2015 13:39:01 CET

* Author :  Kirill

* Sprintnumber : 2, 5

* Backlog entry :

"""
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from app.models import projecttemplate, folder, collaboration
from django.conf import settings

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

    def cloneProject(self, **kwargs):
        if 'project' not in kwargs:
            raise AttributeError('Project ist nicht eingegeben')

        project = kwargs['project']
        newProject = self.create(name=kwargs.get('name', project.name),
                                 author=kwargs.get('author', project.author))

        folder.Folder.objects.copy(project.rootFolder, newProject.rootFolder)
        return newProject


class Project(projecttemplate.ProjectTemplate):
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Collaboration', through_fields=('project', 'user'))
    objects = ProjectManager()

    def getAllCollaborators(self):
        return self.collaborators.all()

    def getConfirmedCollaborators(self):
        collaborations = collaboration.Collaboration.objects.filter(project=self, isConfirmed=True)
        return [c.user for c in collaborations]

    def getUnconfirmedCollaborators(self):
        collaborations = collaboration.Collaboration.objects.filter(project=self, isConfirmed=False)
        return [c.user for c in collaborations]


##
# Automatische Erzeugung des Rootverzeichnises
@receiver(pre_save, sender=Project)
def projectPreSave(instance, **kwargs):
    projecttemplate.projectTemplatePreSave(instance, **kwargs)
