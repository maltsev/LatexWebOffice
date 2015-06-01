# -*- coding: utf-8 -*-
"""

* Purpose : Test des BinaryFile-Modells (app/models/file/binaryfile.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 27 Nov 2014 21:31:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import tempfile, os
from settings import BASE_DIR
from app.models.file.binaryfile import BinaryFile
from app.tests.server.models.modeltestcase import ModelTestCase

class BinaryFileTestCase(ModelTestCase):
    testBinaryFilepath = os.path.join(BASE_DIR, 'app', 'static', 'img', 'icon.png')


    def setUp(self):
        self.setUpProject()


    def test_getContent(self):
        sourceCode = u'Straße, ändern, tést'
        tmpfile, filepath = tempfile.mkstemp()
        file = open(filepath, 'wb')
        file.write(sourceCode.encode('UTF-8'))
        file.close()

        binaryFileModel = BinaryFile.objects.create(name='readme.txt', filepath=filepath,
                                                    folder=self.rootFolder_dir1)
        binaryFile = binaryFileModel.getContent()
        self.assertEqual(sourceCode, binaryFile.readline().decode('utf-8'))
        binaryFile.close()
        os.close(tmpfile)
        binaryFileModel.delete()

        self.assertFalse(os.path.isfile(filepath))


    def test_createFromFile(self):
        file = open(self.testBinaryFilepath, 'rb')
        binaryFileModel = BinaryFile.objects.createFromFile(name='icon.png',
                                                            folder=self.rootFolder_dir1,
                                                            file=file)

        file.seek(0)
        binaryFile = binaryFileModel.getContent()
        self.assertEqual(file.read(), binaryFile.read())
        file.close()
        binaryFile.close()
        binaryFileModel.delete()


    def test_createFromRequestFile(self):
        class RequestFileStub:
            def __init__(self, filepath):
                self.file = open(filepath, 'rb')

            def chunks(self):
                return [line for line in self.file]

            def close(self):
                if self.file:
                    self.file.close()


        requestFileStub = RequestFileStub(self.testBinaryFilepath)
        binaryFileModel = BinaryFile.objects.createFromRequestFile(name='icon.png',
                                                                   folder=self.rootFolder_dir1,
                                                                   requestFile=requestFileStub)
        requestFileStub.close()

        file = open(self.testBinaryFilepath, 'rb')
        binaryFile = binaryFileModel.getContent()
        self.assertEqual(file.read(), binaryFile.read())
        file.close()
        binaryFile.close()
        binaryFileModel.delete()
