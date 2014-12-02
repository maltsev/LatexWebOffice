"""

* Purpose : Test des BinaryFile-Modells (app/models/binaryfile.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 27 Nov 2014 21:31:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import tempfile, os
from core.settings import BASE_DIR
from app.models.file.binaryfile import BinaryFile
from app.tests.server.models.modeltestcase import ModelTestCase

class BinaryFileTestCase(ModelTestCase):
    testBinaryFilepath = os.path.join(BASE_DIR, 'app', 'static', 'img', 'icon.png')


    def setUp(self):
        self.setUpProject()


    def test_getContent(self):
        sourceCode = 'Straße, ändern, tést'
        _, filepath = tempfile.mkstemp()
        file = open(filepath, 'wb')
        file.write(bytearray(sourceCode, 'utf-8'))
        file.close()

        binaryFile = BinaryFile.objects.create(name='readme.txt', filepath=filepath, folder=self.rootFolder_dir1)
        self.assertEqual(sourceCode, binaryFile.getContent().readline().decode('utf-8'))
        binaryFile.delete()

        self.assertFalse(os.path.isfile(filepath))


    def test_createFromFile(self):
        file = open(self.testBinaryFilepath, 'rb')
        binaryFile = BinaryFile.objects.createFromFile(name='icon.png', folder=self.rootFolder_dir1, file=file)

        file.seek(0)
        self.assertEqual(file.read(), binaryFile.getContent().read())
        binaryFile.delete()


    def test_createFromRequestFile(self):
        class RequestFileStub:
            def __init__(self, filepath):
                self.file = open(filepath, 'rb')

            def chunks(self):
                return [line for line in self.file]


        requestFileStub = RequestFileStub(self.testBinaryFilepath)
        binaryFile = BinaryFile.objects.createFromRequestFile(name='icon.png', folder=self.rootFolder_dir1, requestFile=requestFileStub)

        file = open(self.testBinaryFilepath, 'rb')
        self.assertEqual(file.read(), binaryFile.getContent().read())
        binaryFile.delete()
