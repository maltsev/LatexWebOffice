# -*- coding: utf-8 -*-
"""

* Purpose : Test des PlainTextFile-Modells (app/models/file/plaintextfile.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 27 Nov 2014 21:31:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from app.models.file.plaintextfile import PlainTextFile
from app.tests.server.models.modeltestcase import ModelTestCase
from app.common import util

class PlainTextFileTestCase(ModelTestCase):
    def setUp(self):
        self.setUpProject()


    def test_getContent(self):
        sourceCode = 'Straße, ändern, tést'
        plainTextFileModel = PlainTextFile.objects.create(name='readme.txt', source_code=sourceCode, folder=self.rootFolder_dir1)
        plainTextFile = plainTextFileModel.getContent()
        filesize = plainTextFileModel.size
        self.assertEqual(filesize, util.getFileSize(plainTextFile))
        self.assertEqual(sourceCode, plainTextFile.getvalue())
        plainTextFile.close()

        sourceCode = 'Neuer TexCode.'
        plainTextFileModel.source_code = sourceCode
        plainTextFileModel.save()
        plainTextFile = plainTextFileModel.getContent()
        filesize = plainTextFileModel.size
        self.assertEqual(filesize, util.getFileSize(plainTextFile))
        self.assertEqual(sourceCode, plainTextFile.getvalue())
        plainTextFile.close()