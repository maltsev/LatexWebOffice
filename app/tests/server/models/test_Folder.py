# -*- coding: utf-8 -*-
"""

* Purpose : Test des Verzeichnismodells (app/models/folder.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 26 Nov 2014 20:39:13 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import os
import shutil
from django.core.exceptions import ObjectDoesNotExist
from core import settings
from app.models.folder import Folder
from app.models.file.texfile import TexFile
from app.tests.server.models.modeltestcase import ModelTestCase

class FolderTestCase(ModelTestCase):
    def setUp(self):
        self.root = root = Folder.objects.create(name='root')
        self.root_file1 = TexFile.objects.create(name='root_file1', folder=root, source_code='file1')

        self.root_dir1 = Folder.objects.create(name='root_dir1', parent=root, root=root)
        self.root_dir1_file1 = TexFile.objects.create(name='root_dir1_file1', folder=self.root_dir1, source_code='file1')

        self.root_dir2 = Folder.objects.create(name='root_dir2', parent=root, root=root)

        self.root_dir1_dir1 = Folder.objects.create(name='root_dir1_dir1', parent=self.root_dir1, root=root)

        self.root_dir1_dir1_dir1 = Folder.objects.create(name='root_dir1_dir1_dir1', parent=self.root_dir1_dir1, root=root)
        self.root_dir1_dir1_dir1_file1 = TexFile.objects.create(name='root_dir1_dir1_dir1_file1',
                                                                folder=self.root_dir1_dir1_dir1, source_code='file1')
        self.root_dir1_dir1_dir1_file2 = TexFile.objects.create(name='root_dir1_dir1_dir1_file2',
                                                                folder=self.root_dir1_dir1_dir1, source_code='file2')

    def tearDown(self):
        shutil.rmtree(self.root.getTempPath())


    def test_getRoot(self):
        self.assertEqual(self.root, self.root_dir1_dir1_dir1.getRoot())
        self.assertEqual(self.root, self.root.getRoot())


    def test_cascadeDelete(self):
        self.root.delete()

        folders = [self.root, self.root_dir1, self.root_dir2, self.root_dir1_dir1, self.root_dir1_dir1_dir1]
        for folder in folders:
            self.assertRaises(ObjectDoesNotExist, Folder.objects.get, pk=folder.id)

        files = [self.root_file1, self.root_dir1_file1, self.root_dir1_dir1_dir1_file1, self.root_dir1_dir1_dir1_file2]
        for file in files:
            self.assertRaises(ObjectDoesNotExist, TexFile.objects.get, pk=file.id)


    def test_getFilesAndFoldersRecursively(self):
        rootFilesAndFolders = [self.root_file1, self.root.getMainTex(), self.root_dir1, self.root_dir1_file1,
                               self.root_dir2, self.root_dir1_dir1, self.root_dir1_dir1_dir1,
                               self.root_dir1_dir1_dir1_file1, self.root_dir1_dir1_dir1_file2]
        sortFunc = lambda obj: obj.name + str(obj.pk)
        rootFilesAndFolders.sort(key=sortFunc)

        self.assertEqual(rootFilesAndFolders, sorted(self.root.getFilesAndFoldersRecursively(), key=sortFunc))


    def test_getTempFilepath(self):
        rootDirpath = os.path.join(settings.PROJECT_ROOT, str(self.root.pk) + '_' + self.root.name)

        self.assertEquals(rootDirpath, self.root.getTempPath())
        self.assertTrue(os.path.exists(rootDirpath))

        filesAndFolders = self.root.getFilesAndFoldersRecursively()
        for fileOrFolder in filesAndFolders:
            fileOrFolderPath = fileOrFolder.getTempPath()
            self.assertTrue(os.path.exists(fileOrFolderPath))

    def test_dumpFolder(self):
        filesAndFolders = [
            ['main.tex'], ['root_file1'], ['root_dir1'], ['root_dir2'],
            ['root_dir1', 'root_dir1_file1'], ['root_dir1', 'root_dir1_dir1'],
            ['root_dir1', 'root_dir1_dir1', 'root_dir1_dir1_dir1'],
            ['root_dir1', 'root_dir1_dir1', 'root_dir1_dir1_dir1', 'root_dir1_dir1_dir1_file1'],
            ['root_dir1', 'root_dir1_dir1', 'root_dir1_dir1_dir1', 'root_dir1_dir1_dir1_file2']
        ]

        self.assertEqual(self.root.getTempPath(), self.root.dumpFolder())
        for fileOrFolder in filesAndFolders:
            pathParts = [self.root.getTempPath()] + fileOrFolder
            path = os.path.join(*pathParts)
            self.assertTrue(os.path.exists(path), "Not exists: {}".format(path))