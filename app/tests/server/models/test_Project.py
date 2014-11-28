"""

* Purpose : Test des Projectmodells (app/models/project.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 26 Nov 2014 20:39:13 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.contrib.auth.models import User
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.tests.server.models.modeltestcase import ModelTestCase

class ProjectTestCase(ModelTestCase):
    def setUp(self):
        self.setUpProject()


    def test_cascadeDeleteRootFolder(self):
        self.rootFolder.delete()
        self.checkCascadeDelete()

    def test_cascadeDeleteProject(self):
        self.project.delete()
        self.checkCascadeDelete()

    def checkCascadeDelete(self):
        self.assertRaises(ObjectDoesNotExist, Project.objects.get, pk=self.project.id)
        self.assertRaises(ObjectDoesNotExist, Folder.objects.get, pk=self.rootFolder.id)
        self.assertRaises(ObjectDoesNotExist, Folder.objects.get, pk=self.rootFolder_dir1.id)
        self.assertRaises(ObjectDoesNotExist, File.objects.get, pk=self.rootFolder_dir1_file1.id)