# -*- coding: utf-8 -*-
"""

* Purpose : Allgemeine ModelTestCase

* Creation Date : 26-11-2014

* Last Modified : Do 26 Feb 2015 17:39:54 CET

* Author :  maltsev

* Sprintnumber : 3

* Backlog entry :

"""
import os
from django.test import TestCase
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from django.contrib.auth import get_user_model
User = get_user_model()


class ModelTestCase(TestCase):
    def setUpProject(self):
        self.author = User.objects.create_user('admin@admin.com', password='123')

        self.project = Project.objects.create(name='LatexWebOffice', author=self.author)
        self.rootFolder = self.project.rootFolder
        self.mainTexFile = self.rootFolder.getMainTex()

        self.rootFolder_dir1 = Folder.objects.create(name='rootFolder_dir1', parent=self.rootFolder, root=self.rootFolder)
        self.rootFolder_dir1_file1 = File.objects.create(name='rootFolder_dir1_file1', folder=self.rootFolder_dir1)





def getFolderContent(folder):
    return sorted([getFileOrFolderData(f) for f in folder.getFilesAndFoldersRecursively()])


def getFileOrFolderData(file):
    data = str(file).split(os.path.sep)[1:]
    if hasattr(file, 'getContent'):
        contentObj = file.getContent()
        if hasattr(contentObj, 'getvalue'):
            content = contentObj.getvalue()
        else:
            content = contentObj.read()

        data.append(content)

    return data
