"""

* Purpose : Test des File Views und zugehöriger Methoden (app/views/file.py)

* Creation Date : 26-11-2014

* Last Modified : Mi 26 Nov 2014 14:58:13 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : -

"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
from django.conf import settings
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common import util
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
import os


class FileTestClass(TestCase):
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
        self._user2_project1_root = Folder(name='user2_project1')
        self._user2_project1_root.save()

        # erstelle ein Projekt als user1
        self._user1_project1 = Project.objects.create(name='USer1_project1', author=self._user1,
                                                      rootFolder=self._user1_project1_root)
        self._user1_project1.save()

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

        # Erstelle eine .tex Datei für user1 in user1_project1_root (Projekt root Verzeichnis)
        self._user1_tex1 = TexFile(name='main.tex', folder=self._user1_project1_root, source_code='user1_tex1\n')
        self._user1_tex1.save()

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

        # Erstelle eine .tex Datei für user1 in user1_project1_root (Projekt root Verzeichnis)
        self._user2_tex1 = TexFile(name='main.tex', folder=self._user2_project1_root, source_code='user2_tex1\n')
        self._user2_tex1.save()

        self._user1_tex1_newcode = 'user1_tex1\n\nnew text added'
        self._user1_tex1_newname = 'newmain.tex'
        self._user1_binary1_newname = 'newtest.bin'

        # print(Project.objects.get(name__iexact='user1_project1'))


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass


    # Teste das Erstellen einer neuen leeren .tex Datei
    def test_createtexfile(self):
        # Sende Anfrage zum erstellen einer neuen .tex Datei
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name='newmain.tex')

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        serveranswer = {'id': 4, 'name': self._user1_tex1_newname}
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # Sende Anfrage zum erstellen der Datei als user1 mit der folderid die user2 gehört
        response = util.documentPoster(self, command='createtex', idpara=self._user2_project1_folder1.id,
                                       name='newname')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum erstellen der Datei als user1 mit einer folderid die nicht existiert
        response = util.documentPoster(self, command='createtex', idpara=100000, name='newname')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['DIRECTORYNOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['DIRECTORYNOTEXIST'])

        # Sende Anfrage zum erstellen der Datei als user1 mit einem ungültigen Namen
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name='file1<>.tex')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTCREATED'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['INVALIDNAME'])


    # Teste das Ändern einer Datei
    # (source code wurde geändert)
    def test_updatefile(self):
        # Sende Anfrage zum ändern der Datei
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_tex1.id,
                                       content=self._user1_tex1_newcode)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # die in der Datenbank gespeicherte .tex Datei sollte als source_code nun den neuen Inhalt besitzen
        self.assertEqual(TexFile.objects.get(id=self._user1_tex1.id).source_code, self._user1_tex1_newcode)

        # Sende Anfrage zum ändern der Datei mit der fileid einer Binärdatei
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_binary1.id,
                                       content=self._user1_tex1_newcode)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOPLAINTEXTFILE'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOPLAINTEXTFILE'])

        # Sende Anfrage zum ändern der Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='updatefile', idpara=self._user2_tex1.id,
                                       content=self._user1_tex1_newcode)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum ändern der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_invalidid,
                                       content=self._user1_tex1_newcode)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    # Teste das Löschen einer Datei
    def test_deletefile(self):
        # Sende Anfrage zum Löschen der .tex Datei
        response = util.documentPoster(self, command='deletefile', idpara=self._user1_tex1.id)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        self.assertFalse(PlainTextFile.objects.filter(id=self._user1_tex1.id).exists())

        # Sende Anfrage zum Löschen der Binärdatei
        response = util.documentPoster(self, command='deletefile', idpara=self._user1_binary1.id)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        self.assertFalse(BinaryFile.objects.filter(id=self._user1_binary1.id).exists())

        # Sende Anfrage zum Löschen einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='deletefile', idpara=self._user2_tex1.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum Löschen der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='deletefile', idpara=self._user1_invalidid)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    # Teste das umbennen einer Datei
    def test_renamefile(self):
        # Sende Anfrage zum Umbenennen der .tex Datei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex1.id,
                                       name=self._user1_tex1_newname)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.name, self._user1_tex1_newname)

        # Sende Anfrage zum Umbenennen der Binärdatei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_binary1.id,
                                       name=self._user1_binary1_newname)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        userbinobj = BinaryFile.objects.get(id=self._user1_binary1.id)
        self.assertEqual(userbinobj.name, self._user1_binary1_newname)

        # Sende Anfrage zum Umbennen einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='renamefile', idpara=self._user2_tex1.id,
                                       name=self._user1_tex1_newname)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum Umbenennen der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_invalidid,
                                       name=self._user1_tex1_newname)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    # Teste das Verschieben einer Datei
    def test_movefile(self):
        # Sende Anfrage zum Verschieben der .tex Datei in den Unterorder folder1 des Projektes
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex1.id,
                                       idpara2=self._user1_project1_folder1.id)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # die .tex Datei sollte nun in folder 2 sein
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.folder, self._user1_project1_folder1)

        # Sende Anfrage zum Verschieben der Binärdatei in den Unterorder folder1 des Projektes
        response = util.documentPoster(self, command='movefile', idpara=self._user1_binary1.id,
                                       idpara2=self._user1_project1_folder2.id)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # die Binärdatei sollte nun in folder 2 sein
        userbinobj = BinaryFile.objects.get(id=self._user1_binary1.id)
        self.assertEqual(userbinobj.folder, self._user1_project1_folder2)

        # Sende Anfrage zum Verschieben einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='movefile', idpara=self._user2_tex1.id,
                                       idpara2=self._user1_project1_folder1.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum Verschieben der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='movefile', idpara=self._user1_invalidid,
                                       idpara2=self._user1_project1_folder1.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    # Teste upload lokaler Dateien auf den Server
    def test_uploadfiles(self):
        pass


    # Teste download von Dateien auf dem Server zum Client
    def test_downloadfile(self):
        # Sende Anfrage zum Downloaden der test.bin Datei
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_binary1.id)

        # überprüfe die Antwort des Servers
        # der Content-Type sollte 'application/octet-stream' sein
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        # Content-Length sollte 'self._user1_binary1_size' sein (Dateigröße in bytes)
        self.assertEqual(response['Content-Length'], str(self._user1_binary1_size))
        # Content-Disposition sollte 'attachment; filename=b'test.bin'' sein
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=b\'test.bin\'')
        # der Inhalt der heruntergeladenen Datei und der Datei auf dem Server sollte übereinstimmen
        self.assertEqual(self._user1_binary1_str, smart_str(response.content))

        # Sende Anfrage zum Downloaden der main.tex Datei
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_tex1.id)

        # überprüfe die Antwort des Servers
        # der Inhalt der heruntergeladenen Datei und der Datei auf dem Server sollte übereinstimmen
        self.assertEqual(self._user1_tex1.source_code, smart_str(response.content))
        # der Content-Type sollte in response enthalten sein
        # Prüfung auf Content-Type gibt je nach OS unterschiedliche Werte zurück
        # Windows: application/x-tex
        # Linux: text/x-tex
        self.assertIn('Content-Type', response)
        # Content-Length sollte 'self._user1_tex1_size' sein (Dateigröße in bytes)
        # self.assertEqual(response['Content-Length'], str(self._user1_tex1_size))
        # Content-Disposition sollte 'attachment; filename=b'test.bin'' sein
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=b\'main.tex\'')

        # Sende Anfrage zum Download einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='downloadfile', idpara=self._user2_tex1.id)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # sollte Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum Verschieben der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_invalidid)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # sollte Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    # Teste das Abrufen von Informationen einer Datei via fileid
    def test_fileInfo(self):
        # Sende Anfrage zu Dateiinformation der test.bin Datei
        response = util.documentPoster(self, command='fileinfo', idpara=self._user1_binary1.id)

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)

        # lese die Antwort des Server ein
        serveranswer = dictionary['response']

        # status sollte 'success' sein
        self.assertEqual(dictionary['status'], SUCCESS)

        # Es sollten richtige Informationen zur Datei zurückgegeben worden sein
        self.assertIn('fileid', serveranswer)
        self.assertIn('filename', serveranswer)
        self.assertIn('folderid', serveranswer)
        self.assertIn('foldername', serveranswer)

        fileobj = self._user1_binary1  # Die Datei, über die Informationen angefordert wurde
        folderobj = self._user1_binary1.folder  # der Ordner, wo fileobj liegt

        # Die zurückgegebenen Informationen sollten mit fileobj und folderobj übereinstimmen
        self.assertEqual(serveranswer['fileid'], fileobj.id)
        self.assertEqual(serveranswer['filename'], fileobj.name)
        self.assertEqual(serveranswer['folderid'], folderobj.id)
        self.assertEqual(serveranswer['foldername'], folderobj.name)


    # Teste das Komiplieren einer .tex Datei
    def test_latexCompile(self):
        # schicke POST request an den Server mit dem compile Befehl und dem zugehörigen Parameter id:fileid
        response = util.documentPoster(self, command='compile', idpara=self._user1_tex1.id)

        # dekodiere den JSON response als dictionary
        dictionary = util.jsonDecoder(response.content)