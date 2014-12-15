# -*- coding: utf-8 -*-
"""

* Purpose : Test des TexFile-Modells (app/models/file/texfile.py)

* Creation Date : 12-12-2014

* Last Modified : Fr 12 Dec 2014 13:40:00 CET

* Author :  christian

* Sprintnumber : 3

* Backlog entry :

"""
from app.models.file.texfile import TexFile
from app.tests.server.models.modeltestcase import ModelTestCase
from app.common import util

class TexFileTestCase(ModelTestCase):
    def setUp(self):
        self.setUpProject()


    def test_getSize(self):
        sourceCode = 'Straße, ändern, tést'
        texFileModel = TexFile.objects.create(name='newtexfile.tex', source_code=sourceCode, folder=self.rootFolder_dir1)
        texFile = texFileModel.getContent()
        filesize = texFileModel.size
        self.assertEqual(filesize, util.getFileSize(texFile))
        texFile.close()

        sourceCode = 'Neuer TexCode.'
        texFileModel.source_code = sourceCode
        texFileModel.save()
        texFile = texFileModel.getContent()
        filesize = texFileModel.size
        self.assertEqual(filesize, util.getFileSize(texFile))
        texFile.close()