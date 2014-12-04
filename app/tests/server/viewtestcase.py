"""

* Purpose : Test des Projectmodells (app/models/project.py)

* Creation Date : 26-11-2014

* Last Modified : Fri 28 Nov 2014 10:41:36 PM CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import io
import tempfile
import os

from django.test import TestCase
from django.contrib.auth.models import User

from app.models.folder import Folder
from app.models.project import Project
from app.models.file.texfile import TexFile
from app.models.file.binaryfile import BinaryFile


class ViewTestCase(TestCase):
    # Setup Methode für Benutzer und Projekte
    def setUpUserAndProjects(self):
        # erstelle user1
        self._user1 = User.objects.create_user(username='user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'

        # erstelle user2
        self._user2 = User.objects.create_user('user2@test.de', password='test123')
        self._user2._unhashedpw = 'test123'

        # erstelle user3
        self._user3 = User.objects.create_user('user3@test.de', password='test123')
        self._user3._unhashedpw = 'test123'

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

        # erstelle ein Projekt als user1
        self._user1_project1 = Project.objects.create(name='user1_project1', author=self._user1)
        self._user1_project1.save()
        self._user1_project2 = Project.objects.create(name='user1_project2', author=self._user1)
        self._user1_project2.save()

        # erstelle ein Projekt als user2
        self._user2_project1 = Project.objects.create(name='user2_project1', author=self._user2)
        self._user2_project1.save()
        self._user2_project2 = Project.objects.create(name='user2_project2', author=self._user2)
        self._user2_project2.save()


    def setUpSingleUser(self):
        # erstelle user1
        self._user1 = User.objects.create_user(username='user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)


    # Setup Methode für Dateien und Ordner
    def setUpFolders(self):
        # erstelle zwei Order für user1, die dem Projekt user1_project1 zugewiesen werden
        # erstelle einen Unterordner in _user1_project1_folder2
        self._user1_project1_folder1 = Folder(name='user1_project1_folder1', parent=self._user1_project1.rootFolder,
                                              root=self._user1_project1.rootFolder)
        self._user1_project1_folder1.save()
        self._user1_project1_folder2 = Folder(name='user1_project1_folder2', parent=self._user1_project1.rootFolder,
                                              root=self._user1_project1.rootFolder)
        self._user1_project1_folder2.save()
        self._user1_project1_folder2_subfolder1 = Folder(name='user1_project1_folder2_subfolder1',
                                                         parent=self._user1_project1_folder2,
                                                         root=self._user1_project1.rootFolder)
        self._user1_project1_folder2_subfolder1.save()

        # erstelle einen Order für user2, die dem Projekt user2_project1 zugewiesen werden
        # erstelle einen Unterordner in _user2_project1_folder1
        self._user2_project1_folder1 = Folder(name='user2_project1_folder1', parent=self._user2_project1.rootFolder,
                                              root=self._user2_project1.rootFolder)
        self._user2_project1_folder1.save()
        self._user2_project1_folder1_subfolder1 = Folder(name='user2_project1_folder1_subfolder1',
                                                         parent=self._user2_project1_folder1,
                                                         root=self._user1_project1.rootFolder)
        self._user2_project1_folder1_subfolder1.save()


    def setUpFiles(self):
        # Erstelle eine .tex Datei für user1 in user1_project1_root (Projekt root Verzeichnis)
        self._user1_tex1 = self._user1_project1.rootFolder.getMainTex()
        self._user1_tex1.source_code = "\\documentclass[a4paper,10pt]{article} \\usepackage[utf8]{inputenc} \\title{test} \\begin{document} \\maketitle \\begin{abstract} \\end{abstract} \\section{} \\end{document}"
        self._user1_tex1.save()
        self._user1_tex2 = TexFile(name='tex2.tex', folder=self._user1_project1.rootFolder, source_code='user1_tex2\n')
        self._user1_tex2.save()
        self._user1_tex3 = TexFile(name='TEX2.tex', folder=self._user1_project1_folder1, source_code='user1_tex3\n')
        self._user1_tex3.save()

        # Erstelle eine Binärdatei für user1 in user1_project1_folder2_subfolder1
        self._user1_binary1_str = 'user1_binary1-test1.bin'
        user1_binfile1 = io.BytesIO(bytes(self._user1_binary1_str, 'utf-8'))
        self._user1_binary1 = BinaryFile.objects.createFromFile(name='test1.bin',
                                                                folder=self._user1_project1_folder2_subfolder1,
                                                                file=user1_binfile1)
        user1_binfile1.close()

        # Erstelle eine weitere Binärdatei für user1 in user1_project1_folder2_subfolder1
        self._user1_binary2_str = 'user1_binary2-test2.bin'
        user1_binfile2 = io.BytesIO(bytes(self._user1_binary1_str, 'utf-8'))
        self._user1_binary2 = BinaryFile.objects.createFromFile(name='test2.bin',
                                                                folder=self._user1_project1_folder2_subfolder1,
                                                                file=user1_binfile2)
        user1_binfile2.close()

        # Erstelle eine BildDatei für user1 in user1_project1_folder2_subfolder2
        self._user1_binary3_str = 'user1_binary3-test3.jpg'
        user1_binfile3 = io.BytesIO(bytes(self._user1_binary3_str, 'utf-8'))
        self._user1_binary3 = BinaryFile.objects.createFromFile(name='test3.jpg',
                                                                folder=self._user1_project1_folder2_subfolder1,
                                                                file=user1_binfile3)
        user1_binfile3.close()

        # Erstelle eine .tex Datei für user2 in user2_project1_root (Projekt root Verzeichnis)
        self._user2_tex1 = self._user2_project1.rootFolder.getMainTex()
        self._user2_tex1.source_code = 'user2_tex1\n'
        self._user2_tex1.save()

    # Setup Methode für Dateien, die direkt auf der Festplatte vorhanden sein sollen
    # (wird von test_file -> test_uploadfiles() verwendet
    def setUpHddFiles(self):
        self._tmp_filepath = tempfile.mkdtemp()
        self._user1_binfile1_filename = 'test1.bin'
        self._user1_binfile1_filepath = os.path.join(self._tmp_filepath, self._user1_binfile1_filename)
        self._user1_binfile1 = open(self._user1_binfile1_filepath, 'wb')
        self._user1_binfile1.write(b'test_binary')
        self._user1_binfile1.close()

        self._user1_binfile2_filepath = os.path.join(self._tmp_filepath, 'test2.tex')
        self._user1_binfile2 = open(self._user1_binfile2_filepath, 'w')
        self._user1_binfile2.write('test_tex')
        self._user1_binfile2.close()

        self._user1_binfile3_filepath = os.path.join(self._tmp_filepath, 'test3.jpg')
        self._user1_binfile3 = open(self._user1_binfile3_filepath, 'wb')
        self._user1_binfile3.write(b'test_jpg')
        self._user1_binfile3.close()

    # setzt einige Variablen, die in den Tests verwendet werden können
    def setUpValues(self):
        self._new_code1 = 'user1_tex1 new text added'
        self._newtex_name1 = 'newmain.tex'
        self._newbinary_name1 = 'newtest.bin'
        self._invalidid = 100000000
        self._newprojectname1 = 'LatexWebOffice Testprojekt'
        self._newprojectname2 = 'user1_project3'
        self._newprojectname3 = 'user1_project4'


    # entfernt die erstellten Dateien und das Temp Verzeichnis wieder
    def tearDownHddFiles(self):
        if os.path.isfile(self._user1_binfile1_filepath):
            os.remove(self._user1_binfile1_filepath)
        if os.path.isfile(self._user1_binfile2_filepath):
            os.remove(self._user1_binfile2_filepath)
        if os.path.isfile(self._user1_binfile3_filepath):
            os.remove(self._user1_binfile3_filepath)
        if os.path.isdir(self._tmp_filepath):
            os.rmdir(self._tmp_filepath)

    # ruft die delete Methode der binaryfiles auf, damit die Dateien außerhalb
    # der Datenbank auch gelöscht werden
    def tearDownFiles(self):
        self._user1_binary1.delete()
        self._user1_binary2.delete()
        self._user1_binary3.delete()