# -*- coding: utf-8 -*-
"""

* Purpose : Test des PDF-Modells (app/models/file/pdf.py)

* Creation Date : 01-12-2014

* Last Modified : 1 Dec 2014 14:46:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import tempfile, os
from core.settings import BASE_DIR
from app.models.file.pdf import PDF
from app.tests.server.models.modeltestcase import ModelTestCase

class PDFTestCase(ModelTestCase):
    testBinaryFilepath = os.path.join(BASE_DIR, 'app', 'static', 'img', 'icon.png')


    def setUp(self):
        self.setUpProject()


    def test_createFromFile(self):
        file = open(self.testBinaryFilepath, 'rb')
        pdfFileModel = PDF.objects.createFromFile(name='icon.png', folder=self.rootFolder_dir1, file=file)

        file.seek(0)

        pdfFile = pdfFileModel.getContent()
        self.assertEqual(file.read(), pdfFile.read())

        pdfFile.close()
        file.close()
        pdfFileModel.delete()