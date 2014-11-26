"""

* Purpose : Test des Projectmodells (app/view/documents.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 26 Nov 2014 20:39:13 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from django.test import TestCase
from django.contrib.auth.models import User
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from django.core.exceptions import ObjectDoesNotExist

class ProjectTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='admin@admin.com', password='123')
        self.rootFolder = Folder.objects.create(name='rootFolder')
        self.rootFolder_dir1 = Folder.objects.create(name='rootFolder_dir1', parent=self.rootFolder, root=self.rootFolder)
        self.rootFolder_dir1_file1 = File.objects.create(name='rootFolder_dir1_file1', folder=self.rootFolder_dir1)

        self.project = Project.objects.create(name='LatexWebOffice', author=self.author, rootFolder=self.rootFolder)


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