"""

* Purpose : Test des BinaryFile-Modells (app/models/binaryfile.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 27 Nov 2014 21:31:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import tempfile, os
from app.models.file.binaryfile import BinaryFile
from app.tests.server.models.modeltestcase import ModelTestCase

class BinaryFileTestCase(ModelTestCase):
    def setUp(self):
        self.setUpProject()


    def test_getContent(self):
        sourceCode = 'Straße, ändern, tést'
        _, filepath = tempfile.mkstemp()
        file = open(filepath, 'w')
        file.write(sourceCode)
        file.close()

        binaryFile = BinaryFile.objects.create(name='readme.txt', filepath=filepath, folder=self.rootFolder_dir1)
        self.assertEqual(sourceCode, binaryFile.getContent().readline())
        binaryFile.delete()

        self.assertFalse(os.path.isfile(filepath))
