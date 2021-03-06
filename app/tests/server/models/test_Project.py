# -*- coding: utf-8 -*-
"""

* Purpose : Test des Projectmodells (app/models/project.py)

* Creation Date : 26-11-2014

* Last Modified : 17 Dec 2014 10:02:00 CET

* Author :  maltsev

* Sprintnumber : 3

* Backlog entry :

"""
from django.core.exceptions import ObjectDoesNotExist
from app.models.folder import Folder
from app.models.project import Project
from app.models.projecttemplate import ProjectTemplate
from app.models.file.file import File
from app.tests.server.models.test_ProjectTemplate import ProjectTemplateTestCase
from app.tests.server.models import modeltestcase

class ProjectTestCase(ProjectTemplateTestCase):
    def test_createFromProjectTemplate(self):
        projectTemplate = ProjectTemplate.objects.get(pk=self.project.pk)
        projectTemplateName = projectTemplate.name
        project = Project.objects.createFromProjectTemplate(template=projectTemplate, name="Testprojekt")

        self.assertEqual("Testprojekt", project.name)
        self.assertEqual(projectTemplateName, projectTemplate.name)

        projectRootFolderContent = modeltestcase.getFolderContent(self.project.rootFolder)
        projectTemplateRootFolderContent = modeltestcase.getFolderContent(projectTemplate.rootFolder)

        self.assertEqual(projectRootFolderContent, projectTemplateRootFolderContent)

        projectTemplateRootFolderMainTex = projectTemplate.rootFolder.getMainTex()
        projectTemplateRootFolderMainTex.source_code = projectTemplateRootFolderMainTex.source_code + 'test'
        projectTemplateRootFolderMainTex.save()

        self.assertNotEqual(projectTemplateRootFolderContent, modeltestcase.getFolderContent(projectTemplate.rootFolder))
        self.assertEqual(projectRootFolderContent, modeltestcase.getFolderContent(project.rootFolder))


    def test_getProject(self):
        self.assertEqual(self.project, self.rootFolder.getProject())
        self.assertEqual(self.project, self.rootFolder_dir1.getProject())

    def test_cascadeDeleteRootFolder(self):
        self.rootFolder.delete()
        self.checkCascadeDelete()

    def test_cascadeDeleteProject(self):
        self.project.delete()
        self.checkCascadeDelete()

    def checkCascadeDelete(self):
        self.assertRaises(ObjectDoesNotExist, ProjectTemplate.objects.get, pk=self.project.pk)
        self.assertRaises(ObjectDoesNotExist, Project.objects.get, pk=self.project.pk)
        self.assertRaises(ObjectDoesNotExist, Folder.objects.get, pk=self.rootFolder.pk)
        self.assertRaises(ObjectDoesNotExist, Folder.objects.get, pk=self.rootFolder_dir1.pk)
        self.assertRaises(ObjectDoesNotExist, File.objects.get, pk=self.rootFolder_dir1_file1.pk)
        self.assertRaises(ObjectDoesNotExist, File.objects.get, pk=self.mainTexFile.pk)