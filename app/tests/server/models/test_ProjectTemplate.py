# -*- coding: utf-8 -*-
"""

* Purpose : Test des ProjectTemplate-Modells (app/models/projecttemplate.py)

* Creation Date : 11-12-2014

* Last Modified : 17 Dev 2014 10:01:13 CET

* Author :  maltsev

* Sprintnumber : 3

* Backlog entry :

"""
from app.models.projecttemplate import ProjectTemplate
from app.tests.server.models import modeltestcase

class ProjectTemplateTestCase(modeltestcase.ModelTestCase):
    def setUp(self):
        self.setUpProject()

    def test_createFromProject(self):
        project = self.project
        projectName = project.name
        projectTemplate = ProjectTemplate.objects.createFromProject(project=project, name="Projektvorlage")

        self.assertEqual("Projektvorlage", projectTemplate.name)
        self.assertEqual(projectName, project.name)

        projectRootFolderContent = modeltestcase.getFolderContent(project.rootFolder)
        projectTemplateRootFolderContent = modeltestcase.getFolderContent(projectTemplate.rootFolder)
        self.assertEqual(projectRootFolderContent, projectTemplateRootFolderContent)

        projectRootFolderMainTex = project.rootFolder.getMainTex()
        projectRootFolderMainTex.source_code = projectRootFolderMainTex.source_code + " test"
        projectRootFolderMainTex.save()

        self.assertNotEqual(projectRootFolderContent, modeltestcase.getFolderContent(project.rootFolder))
        self.assertEqual(projectTemplateRootFolderContent, modeltestcase.getFolderContent(projectTemplate.rootFolder))