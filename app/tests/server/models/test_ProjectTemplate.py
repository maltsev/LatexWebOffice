# -*- coding: utf-8 -*-
"""

* Purpose : Test des ProjectTemplate-Modells (app/models/projecttemplate.py)

* Creation Date : 11-12-2014

* Last Modified : 11 Dev 2014 20:26:13 CET

* Author :  maltsev

* Sprintnumber : 3

* Backlog entry :

"""
from app.models.projecttemplate import ProjectTemplate
from app.tests.server.models.modeltestcase import ModelTestCase

class ProjectTemplateTestCase(ModelTestCase):
    def setUp(self):
        self.setUpProject()

    def test_createFromProject(self):
        projectTemplate = ProjectTemplate.objects.createFromProject(project=self.project, name="Projektvorlage")

        self.assertEqual("Projektvorlage", projectTemplate.name)
        self.assertEqual(len(self.project.rootFolder.getFilesAndFoldersRecursively()),
                         len(projectTemplate.rootFolder.getFilesAndFoldersRecursively()))
