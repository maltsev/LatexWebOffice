# -*- coding: utf-8 -*-
"""

* Purpose : Allgemeine ModelTestCase

* Creation Date : 26-11-2014

* Last Modified : Fri 28 Nov 2014 10:41:36 PM CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from django.test import TestCase
from django.contrib.auth.models import User
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File

class ModelTestCase(TestCase):
    def setUpProject(self):
        self.author = User.objects.create_user(username='admin@admin.com', password='123')

        self.project = Project.objects.create(name='LatexWebOffice', author=self.author)
        self.rootFolder = self.project.rootFolder
        self.mainTexFile = self.rootFolder.getMainTex()

        self.rootFolder_dir1 = Folder.objects.create(name='rootFolder_dir1', parent=self.rootFolder, root=self.rootFolder)
        self.rootFolder_dir1_file1 = File.objects.create(name='rootFolder_dir1_file1', folder=self.rootFolder_dir1)
