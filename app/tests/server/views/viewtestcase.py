# -*- coding: utf-8 -*-
"""

* Purpose : Test des Projectmodells (app/models/project.py)

* Creation Date : 26-11-2014

* Last Modified : Do 26 Feb 2015 17:41:09 CET

* Author :  maltsev

* Sprintnumber : 2, 3

* Backlog entry :

"""
import os
import shutil

from django.test import TestCase

import settings
from app.models.folder import Folder
from app.models.project import Project
from app.models.projecttemplate import ProjectTemplate
from app.models.file.texfile import TexFile
from app.models.file.binaryfile import BinaryFile
from app.models.collaboration import Collaboration
from app.common.util import getUserModel
User = getUserModel()


class ViewTestCase(TestCase):
    """ Klasse für Test Methoden der einzelnen Views.

    """

    def setUpUserAndProjects(self):
        """Erstellt Benutzer und Projekte für die Tests.

        Es werden 3 Benutzer erstellt:
        - user1 hat 3 Projekte und 2 Vorlagen
        - user2 hat 2 Projekte
        - user3 hat keine Projekte

        :return: None
        """

        # erstelle user1
        self._user1 = User.objects.create_user('user1@test.de', password='123456')
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
        self._user1_project1 = Project.objects.createWithMainTex(name='user1_project1', author=self._user1)
        self._user1_project2 = Project.objects.createWithMainTex(name='user1_project2', author=self._user1)
        self._user1_project3 = Project.objects.createWithMainTex(name='user1_project3', author=self._user1)
        self._user1_project4 = Project.objects.createWithMainTex(name='Übungsprojekt 01', author=self._user1)

        # erstelle eine Vorlage als user1
        self._user1_template1 = ProjectTemplate.objects.create(name='user1_template1', author=self._user1)
        self._user1_template2 = ProjectTemplate.objects.create(name='user1_template2', author=self._user1)
        self._user1_template3 = ProjectTemplate.objects.create(name='user1_template2´3', author=self._user1)

        # erstelle ein Projekt als user2
        self._user2_project1 = Project.objects.createWithMainTex(name='user2_project1', author=self._user2)
        self._user2_project2 = Project.objects.createWithMainTex(name='user2_project2', author=self._user2)
        self._user2_template1 = ProjectTemplate.objects.create(name='user2_template1', author=self._user2)


    def setUpCollaborations(self):
        self._user2_sharedproject = Project.objects.createWithMainTex(name='user2_sharedproject', author=self._user2)
        self._user2_sharedproject_folder1 = Folder.objects.create(name='user2_sharedproject_folder1',
                                                                  parent=self._user2_sharedproject.rootFolder,
                                                                  root=self._user2_sharedproject.rootFolder)
        self._user2_sharedproject_folder2 = Folder.objects.create(name='user2_sharedproject_folder2',
                                                                  parent=self._user2_sharedproject.rootFolder,
                                                                  root=self._user2_sharedproject.rootFolder)

        maintex = self._user2_sharedproject.rootFolder.getMainTex()
        maintex.source_code = 'Hallo!'
        maintex.save()


        self._user2_sharedproject_folder1_texfile = TexFile(name='temp.tex', folder=self._user2_sharedproject_folder1,
                                                    source_code='invalidtex source code')


        Collaboration.objects.create(user=self._user1, project=self._user2_sharedproject, isConfirmed=True)


    def setUpSingleUser(self):
        """Erstellt einen einzelnen Benutzer und loggt diesen ein.

        :return: None
        """

        # erstelle user1
        self._user1 = User.objects.create_user('user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

    def setUpFolders(self):
        """Erstellt mehrere Ordner in den Projekten von user1 und user2.

        Es werden folgende Ordner erstellt:
        user1_project1/folder1
        user1_project1/folder2
        user1_project1/folder2/subfolder1

        user2_project1/folder1
        user2_project1/folder1/subfolder1

        :return: None
        """

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

        # erstelle zwei Order für user1, die dem Projekt user1_project4 zugewiesen werden
        self._user1_project4_folder1 = Folder(name='Übung 01', parent=self._user1_project4.rootFolder,
                                              root=self._user1_project4.rootFolder)
        self._user1_project4_folder1.save()
        self._user1_project4_folder2 = Folder(name='Übung 02', parent=self._user1_project4_folder1,
                                              root=self._user1_project4.rootFolder)
        self._user1_project4_folder2.save()
        self._user1_project4_folder3 = Folder(name='übung 02', parent=self._user1_project4.rootFolder,
                                              root=self._user1_project4.rootFolder)
        self._user1_project4_folder3.save()

        # erstelle zwei Order für user1, die der Vorlage user1_template1 zugewiesen werden
        # erstelle einen Unterordner in _user1_template1_folder2
        self._user1_template1_folder1 = Folder(name='user1_template1_folder1', parent=self._user1_template1.rootFolder,
                                               root=self._user1_template1.rootFolder)
        self._user1_template1_folder1.save()
        self._user1_template1_folder2 = Folder(name='user1_template1_folder2', parent=self._user1_template1.rootFolder,
                                               root=self._user1_template1.rootFolder)
        self._user1_template1_folder2.save()
        self._user1_template1_folder2_subfolder1 = Folder(name='user1_template1_folder2_subfolder1',
                                                          parent=self._user1_template1_folder2,
                                                          root=self._user1_template1.rootFolder)
        self._user1_template1_folder2_subfolder1.save()

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
        """Lädt mehrere Testdateien und speichert diese in der Datenbank.

        Es werden folgende Dateien erstellt:
        - user1: tex1 in project1_rootFolder (main.tex, es wird der sourc_code geändert)
        - user1: tex2 in project1_rootFolder
        - user1: tex3 in project1_rootFolder/folder1
        - user1 : tex4

        :return: None
        """

        # Dateinamen der verwendeten Testdateien
        texfile1_name = 'test_tex_presentation.tex'
        texfile2_name = 'test_tex_simple.tex'
        texfile3_name = 'test_tex_images.tex'
        texfile4_name = 'test_tex_simple.tex'
        texfile5_name = 'test_tex_simple.tex'
        binfile1_name = 'test_bin.bin'
        binfile2_name = 'test_jpg.jpg'
        binfile3_name = 'test_png.png'
        zipfile1_name = 'test_utf8_Übung.zip'

        texfile1_name_specialchars = 'Übungsblatt01.tex'
        texfile2_name_specialchars = 'Übungsblatt02.tex'

        # Pfad für die zip
        self._zipfile1_path = os.path.join(settings.TESTFILES_ROOT, zipfile1_name)

        # Ändere den Source Code der main.tex Datei von user1_project1
        self._user1_tex1 = self._user1_project1.rootFolder.getMainTex()
        texfile1 = open(os.path.join(settings.TESTFILES_ROOT, texfile1_name), 'r')
        self._user1_tex1_source_code = texfile1.read()
        self._user1_tex1.source_code = self._user1_tex1_source_code
        self._user1_tex1.save()

        # Erstelle eine .tex Datei für user1 in user1_project1_root (Projekt root Verzeichnis)
        texfile2 = open(os.path.join(settings.TESTFILES_ROOT, texfile2_name), 'r')
        self._user1_tex2_source_code = texfile2.read()
        self._user1_tex2 = TexFile(name=texfile2_name, folder=self._user1_project1.rootFolder,
                                   source_code=self._user1_tex2_source_code)
        self._user1_tex2.save()

        # Erstelle eine .tex Datei für user1 in user1_project1_folder1
        texfile3 = open(os.path.join(settings.TESTFILES_ROOT, texfile3_name), 'r')
        self._user1_tex3_source_code = texfile3.read()
        self._user1_tex3 = TexFile(name=texfile3_name, folder=self._user1_project1_folder1,
                                   source_code=self._user1_tex3_source_code)
        self._user1_tex3.save()

        # Erstelle eine .tex Datei für user1 in user1_project1_folder1
        self._user1_tex4 = TexFile(name=texfile2_name, folder=self._user1_project1_folder1,
                                   source_code='invalidtex source code')
        self._user1_tex4.save()

        # Erstelle eine .tex Datei für user1 in user1_project4_folder1
        texfile3.seek(0)
        self._user1_tex5_source_code = texfile3.read()
        self._user1_tex5 = TexFile(name=texfile1_name_specialchars, folder=self._user1_project4_folder1,
                                   source_code=self._user1_tex3_source_code)
        self._user1_tex5.save()

        # Erstelle eine .tex Datei für user1 in user1_project4_folder1
        texfile3.seek(0)
        self._user1_tex6_source_code = texfile3.read()
        self._user1_tex6 = TexFile(name=texfile2_name_specialchars, folder=self._user1_project4_folder1,
                                   source_code=self._user1_tex3_source_code)
        self._user1_tex6.save()

        # Erstelle eine Binärdatei für user1 in user1_project1_folder2_subfolder1
        self._user1_binfile1_path = os.path.join(settings.TESTFILES_ROOT, binfile1_name)
        binfile1 = open(self._user1_binfile1_path, 'rb')
        self._user1_binary1 = BinaryFile.objects.createFromFile(name=binfile1_name,
                                                                folder=self._user1_project1_folder2_subfolder1,
                                                                file=binfile1)
        binfile1.close()

        # Ändere den Source Code der main.tex Datei von user2_project1
        self._user2_tex1 = self._user2_project1.rootFolder.getMainTex()
        texfile2 = open(os.path.join(settings.TESTFILES_ROOT, texfile2_name), 'r')
        self._user2_tex1.source_code = texfile2.read()
        self._user2_tex1.save()

        # Erstelle eine jpg Bilddatei für user1 in user1_project1_folder2_subfolder1
        self._user1_binary2_path = os.path.join(settings.TESTFILES_ROOT, binfile2_name)
        binfile2 = open(self._user1_binary2_path, 'rb')
        self._user1_binary2 = BinaryFile.objects.createFromFile(name=binfile2_name,
                                                                folder=self._user1_project1_folder2_subfolder1,
                                                                file=binfile2)
        binfile2.close()

        # Erstelle eine png Bilddatei für user1 in user1_project1_folder2_subfolder2
        self._user1_binary3_path = os.path.join(settings.TESTFILES_ROOT, binfile3_name)
        binfile3 = open(self._user1_binary3_path, 'rb')
        self._user1_binary3 = BinaryFile.objects.createFromFile(name=binfile3_name,
                                                                folder=self._user1_project1_folder2_subfolder1,
                                                                file=binfile3)
        binfile3.close()


    # setzt einige Variablen, die in den Tests verwendet werden können
    def setUpValues(self):
        texfile_name = 'test_tex_simple.tex'
        texfile = open(os.path.join(settings.TESTFILES_ROOT, texfile_name), 'r')
        self._new_code1 = texfile.read()
        texfile.close()
        self._newtex_name1 = 'NeuerTexName1.tex'
        self._newtex_name2 = 'NeuerTexName2.tex'
        self._newtex_name3 = 'NeuerTexName3.tex'
        self._newtex_name_only_ext = '.tex'
        self._newtex_name_specialchars1 = 'übungsblatt 01.tex'
        self._newtex_name_specialchars2 = 'übungsblatt 02.tex'
        self._newbinary_name1 = 'NeuerBinaryName1.bin'
        self._newbinary_name2 = 'NeuerBinaryName2.bin'
        self._newbinary_name3 = 'NeuerBinaryName3.bin'
        self._newname1 = 'NeuerName1'
        self._newname2 = 'NeuerName2'
        self._newname3 = 'NeuerName3'
        self._newname4 = 'NeuerName4'
        self._newname5 = 'NeuerName5'
        self._invalidid = 100000000
        self._name_only_spaces = '    '
        self._name_blank = ''
        self._name_invalid_chars = 'Test1234<>\\/'
        self._name_no_ext = 'filename'
        self._name_only_ext = '.tex'


    # löscht den Ordner für die test Dateien
    def tearDownFiles(self):
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
