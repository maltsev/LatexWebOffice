"""

* Purpose : Test des Verzeichnismodells (app/view/documents.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 26 Nov 2014 20:39:13 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from django.test import TestCase
from app.models.folder import Folder
from app.models.file.file import File
from django.core.exceptions import ObjectDoesNotExist

class FolderTestCase(TestCase):
    def setUp(self):
        self.root = root = Folder.objects.create(name='root')
        self.root_file1 = File.objects.create(name='root_file1', folder=root)

        self.root_dir1 = Folder.objects.create(name='root_dir1', parent=root, root=root)
        self.root_dir1_file1 = File.objects.create(name='root_dir1_file1', folder=self.root_dir1)

        self.root_dir2 = Folder.objects.create(name='root_dir2', parent=root, root=root)

        self.root_dir1_dir1 = Folder.objects.create(name='root_dir1_dir1', parent=self.root_dir1, root=root)

        self.root_dir1_dir1_dir1 = Folder.objects.create(name='root_dir1_dir1_dir1', parent=self.root_dir1_dir1, root=root)
        self.root_dir1_dir1_dir1_file1 = File.objects.create(name='root_dir1_dir1_dir1_file1', folder=self.root_dir1_dir1_dir1)
        self.root_dir1_dir1_dir1_file2 = File.objects.create(name='root_dir1_dir1_dir1_file2', folder=self.root_dir1_dir1_dir1)


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
            self.assertRaises(ObjectDoesNotExist, File.objects.get, pk=file.id)