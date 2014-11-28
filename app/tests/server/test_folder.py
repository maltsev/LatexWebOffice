"""

* Purpose : Test des Folder Views und zugehöriger Methoden (app/views/folder.py)

* Creation Date : 26-11-2014

* Last Modified : Fr 28 Nov 2014 13:19:46 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : -

"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common import util
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from django.conf import settings
import os


class FolderTestClass(TestCase):
    # Initialiserung der benötigten Objekte
    # -> wird vor jedem Test ausgeführt
    def setUp(self):
        # erstelle user1
        self._user1 = User.objects.create_user(
            username='user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'
        self._user1_invalidid = 10000

        # erstelle user2
        self._user2 = User.objects.create_user(
            'user2@test.de', password='test123')
        self._user2._unhashedpw = 'test123'

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

        # erstelle die root Ordner für die einzelnen Projekte
        self._user1_project1_root = Folder(name='user1_project1')
        self._user1_project1_root.save()
        self._user1_project2_root = Folder(name='user1_project2')
        self._user1_project2_root.save()
        self._user2_project1_root = Folder(name='user2_project1')
        self._user2_project1_root.save()

        # erstelle ein Projekt als user1
        self._user1_project1 = Project.objects.create(name='user1_project1', author=self._user1,
                                                      rootFolder=self._user1_project1_root)
        self._user1_project1.save()
        self._user1_project2 = Project.objects.create(name='user1_project2', author=self._user1,
                                                      rootFolder=self._user1_project2_root)
        self._user1_project2.save()

        # erstelle ein Projekt als user2
        self._user2_project1 = Project.objects.create(name='user2_project1', author=self._user2,
                                                      rootFolder=self._user2_project1_root)
        self._user2_project1.save()

        # erstelle zwei Order für user1, die dem Projekt user1_project1 zugewiesen werden
        # erstelle einen Unterordner in _user1_project1_folder2
        self._user1_project1_folder1 = Folder(name='user1_project1_folder1', parent=self._user1_project1_root,
                                              root=self._user1_project1_root)
        self._user1_project1_folder1.save()
        self._user1_project1_folder2 = Folder(name='user1_project1_folder2', parent=self._user1_project1_root,
                                              root=self._user1_project1_root)
        self._user1_project1_folder2.save()
        self._user1_project1_folder2_subfolder1 = Folder(name='user1_project1_folder2_subfolder1',
                                                         parent=self._user1_project1_folder2,
                                                         root=self._user1_project1_root)
        self._user1_project1_folder2_subfolder1.save()

        # erstelle einen Order für user2, die dem Projekt user2_project1 zugewiesen werden
        # erstelle einen Unterordner in _user2_project1_folder1
        self._user2_project1_folder1 = Folder(name='user2_project1_folder1', parent=self._user2_project1_root,
                                              root=self._user2_project1_root)
        self._user2_project1_folder1.save()
        self._user2_project1_folder1_subfolder1 = Folder(name='user2_project1_folder1_subfolder1',
                                                         parent=self._user2_project1_folder1,
                                                         root=self._user2_project1_root)
        self._user2_project1_folder1_subfolder1.save()

        self._user1_dir = os.path.join(settings.FILEDATA_URL, str(self._user1.id))
        self._user1_project1_dir = os.path.join(self._user1_dir, str(self._user1_project1.id))
        if not os.path.isdir(self._user1_project1_dir):
            os.makedirs(self._user1_project1_dir)

        # Erstelle eine Binärdatei für user1 in user1_project1_folder2_subfolder1
        self._user1_binary1 = BinaryFile(name='test.bin', folder=self._user1_project1_folder2_subfolder1)
        self._user1_binary1.save()
        self._user1_binary1_str = 'user1_binary1'
        file_path = os.path.join(self._user1_project1_dir, str(self._user1_binary1.id))
        user1_binfile1 = open(file_path, 'w')
        self._user1_binary1_size = user1_binfile1.write(self._user1_binary1_str)
        user1_binfile1.close()


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass


    # Teste das Erzeugen von Ordnern
    def test_createDir(self):
        # Sende Anfrage zum Erstellen eines Ordners im rootfolder von Projekt 1
        response = util.documentPoster(self, command='createdir', idpara=self._user1_project1.rootFolder.id,
                                       name='testFolder')

        dictionary = util.jsonDecoder(response.content)
        # überprüfe die Antwort des Servers
        # status sollte success sein
        self.assertEqual(dictionary['status'], SUCCESS)

        serveranswer = dictionary['response']

        # antwort sollte id, name, parentfolderid und parentfoldername enthalten
        self.assertIn('id', serveranswer)
        self.assertIn('name', serveranswer)
        self.assertIn('parentfolderid', serveranswer)
        self.assertIn('parentfoldername', serveranswer)
        self.assertTrue(serveranswer['name'], 'testFolder')

        # Teste, ob der Ordner wirklich existiert und mit dem Werten, die zurückgegeben wurden, übereinstimmt
        self.assertTrue(Folder.objects.filter(id=serveranswer['id']).exists())
        self.assertTrue(Folder.objects.filter(name='testFolder').exists())
        folder1 = Folder.objects.get(id=serveranswer['id'])
        # Teste, ob der Ordner im richtigen Projekt erstellt wurde
        self.assertEqual(folder1.getRoot().getProject(), self._user1_project1)

        # Teste, ob ein Unterverzeichnis von einem Unterverzeichnis angelegt werden kann
        # und das auch mit dem gleichen Namen
        response = util.documentPoster(self, command='createdir', idpara=folder1.id, name='root')
        dictionary = util.jsonDecoder(response.content)
        self.assertTrue(Folder.objects.filter(id=dictionary['response']['id']).exists())
        #Teste, ob ein Verzeichnis zwei gleichnamige Unterverzeichnisse haben kann
        response = util.documentPoster(self, command='createdir', idpara=folder1.id, name='root')
        dictionary = util.jsonDecoder(response.content)
        self.assertEqual(dictionary['response'],ERROR_MESSAGES['FOLDERNAMEEXISTS'])

        #Teste, wie es sich mit falschen Angaben verhält

        #Teste ob user1 in einem Project vom user2 ein Verzeichnis erstellen kann
        response = util.documentPoster(self, command='createdir', idpara=self._user2_project1.id, name='IDONOTEXISTDIR')
        dictionary = util.jsonDecoder(response.content)
        self.assertEqual(dictionary['status'], FAILURE)
        #Teste, dass die richtige Fehlermeldung zurückgegeben wird
        dictionaryresponse = dictionary['response']
        self.assertEqual(dictionaryresponse, ERROR_MESSAGES['NOTENOUGHRIGHTS'])
        #Teste, dass das Verzeichnis auch nicht erstellt wurde
        self.assertFalse(Folder.objects.filter(name='IDONOTEXISTDIR').exists())

        #Teste auf leeren Verzeichnisnamen
        response = util.documentPoster(self, command='createdir', idpara=self._user1_project1.id, name=' ')
        dictionary = util.jsonDecoder(response.content)
        serveranswer = dictionary['response']
        self.assertEqual(serveranswer, ERROR_MESSAGES['BLANKNAME'])


    # Teste das Löschen eines Ordners
    # Teste, ob Unterordner und zum Ordner gehörende Dateien auch gelöscht werden
    def test_rmDir(self):
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)
        oldrootfolderid = self._user1_project1.rootFolder.id
        oldtodeletefolder = self._user1_project1_folder2
        oldsubdeletefolder=self._user1_project1_folder2_subfolder1
        oldfileid = self._user1_binary1.id
        # Stelle sicher, dass zu diesem Zeitpunkt der rootordner von project1 noch existiert
        self.assertTrue(Folder.objects.filter(id=oldrootfolderid).exists())
        # Stelle sicher, dass es zu diesem Projekt mind. ein Unterverzeichnis existiert + mind. eine Datei
        self.assertEqual(self._user1_project1_folder1.parent, self._user1_project1.rootFolder)
        self.assertTrue(File.objects.filter(id=oldfileid).exists())

        # Teste, dass man keinen Rootfolder löschen kann
        response = util.documentPoster(self, command='rmdir', idpara=self._user1_project1_root.id)
        dictionary = util.jsonDecoder(response.content)
        serveranswer = dictionary['response']
        self.assertEqual(dictionary['status'], FAILURE)

        # Teste, dass man sonstige Ordner löschen kann
        response=util.documentPoster(self,command='rmdir',idpara=self._user1_project1_folder2.id)

        self.assertFalse(Folder.objects.filter(id=oldtodeletefolder.id).exists())

        # Unterverzeichnisse und Dateien sollten dabei auch gelöscht werden! 
        self.assertFalse(Folder.objects.filter(id=oldsubdeletefolder.id).exists())
        
        # Files von Unterverzeichnissen ebenso
        self.assertFalse(File.objects.filter(id=oldfileid).exists())


    # Teste das Unbenennen von Ordnern
    def test_renameDir(self):
        oldid = self._user1_project1_folder1.id
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder1.id,
                                       name='newname')

        dictionary = util.jsonDecoder(response.content)
        serveranswer = dictionary['response']

        # Teste auf richtige Response Daten bei einer Anfrage, die funktionieren sollte
        self.assertEqual(dictionary['status'], SUCCESS)

        self.assertIn('id', serveranswer)
        self.assertIn('name', serveranswer)

        self.assertEqual(serveranswer['id'], oldid)
        self.assertEqual(serveranswer['name'], 'newname')

        # Teste, ob ein Unterverzeichnis den gleichen Namen haben kann, wie ein anderes Unterverzeichnis
        # im gleichen Elternverzeichnis
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder2.id, name='newname')
        dictionary = util.jsonDecoder(response.content)
        self.assertEqual(dictionary['response'],ERROR_MESSAGES['FOLDERNAMEEXISTS'])

        # Teste, ob ein anderer User das Projekt eines anderen unbenennen kann
        response = util.documentPoster(self, command='renamedir', idpara=self._user2_project1.id, name='ROFL')
        dictionary = util.jsonDecoder(response.content)
        serveranswer = dictionary['response']

        self.assertEqual(dictionary['status'], FAILURE)

        self.assertEqual(ERROR_MESSAGES['NOTENOUGHRIGHTS'], serveranswer)



    # Teste, ob ein Verzeichnis einen leeren Namen haben kann: Überflüssig, da dies bereits schon
    # in der test_createDir Methode getestet wird


    # Teste das Verschieben eines Ordners
    def test_moveDir(self):
        # Sende Anfrage zum verschieben des folder1 in den folder2
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder1.id,
                                       idpara2=self._user1_project1_folder2.id)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        serveranswer = {'id': self._user1_project1_folder1.id,
                        'name': self._user1_project1_folder1.name,
                        'parentid': self._user1_project1_folder2.id,
                        'rootid': self._user1_project1_folder1.root.id}
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        dictionary = util.jsonDecoder(response.content)
        # Teste, ob beim richtiger Anfrage eine Erfolgsmeldung zurückgegeben wird
        self.assertEqual(dictionary['status'], SUCCESS)

        # Teste, ob ob man zwischen Projekten Dateuen verschieben darf (sollte man dürfen)
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder2.id,
                                       idpara2=self._user1_project2.rootFolder.id)
        self.assertEqual(util.jsonDecoder(response.content)['status'], SUCCESS)

        # Teste, dass es eine Fehlermeldung gibt, falls die Datei in einen Ordner verschoben wird,
        # die dem User nicht gehört
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder2.id,
                                       idpara2=self._user2_project1_root)
        self.assertEqual(util.jsonDecoder(response.content)['status'], FAILURE)

        # Teste, ob Fehlermeldung bei falscher fileid
        response = util.documentPoster(self, command='movedir', idpara=-1, idpara2=self._user1_project1_folder2.id)
        self.assertEqual(util.jsonDecoder(response.content)['status'], FAILURE)

    
    # Teste, dass beim Verschieben eines Ordners nach überprüft wird, ob es einen gleichnamigen Unterordner im neuen Parentordner schon gibt 
    def test_moveDir2(self):
        
        # Teste, ob Fehlermeldung, falls es einen gleichnamigen Unterordner im Ordner schon gibt
        # Benenne subfolder so um, dass er den gleichen Namen, wie parentfolder
        self._user1_project1_folder2_subfolder1.name=self._user1_project1_folder2.name
        self._user1_project1_folder2_subfolder1.save()
        # Versuche subfolder in den gleichen Ordner wie parentfolder zu verschieben
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder2_subfolder1.id, idpara2=self._user1_project1_folder2.id)
        dictionary = util.jsonDecoder(response.content)
        self.assertEqual(dictionary['response'],ERROR_MESSAGES['FOLDERNAMEEXISTS'])


    # Teste das Auflisten der Datei- und Ordnerstruktur eines Ordners
    def test_listfiles(self):
        # Anfrage der Struktur von _user1_project1_folder2 (Aufbau siehe SetUp Methode)
        response = util.documentPoster(self, command='listfiles', idpara=self._user1_project1_folder2.id)

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        self.assertEqual(dictionary['status'], SUCCESS)
        # TODO
        # anfrage sollte Ordner/Dateistruktur als Json liefern
        #util.validateJsonSuccessResponse(self, response.content, jsonstr)

        # Anfrage mit user1 auf Ordner von user2
        response = util.documentPoster(self, command='listfiles', idpara=self._user2_project1_root.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Anfrage auf nicht existierenden Ordner
        response = util.documentPoster(self, command='listfiles', idpara=self._user1_invalidid)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte Fehlermeldung ERROR_MESSAGES['DIRECTORYNOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['DIRECTORYNOTEXIST'])