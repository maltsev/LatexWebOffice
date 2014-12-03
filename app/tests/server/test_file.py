"""

* Purpose : Test des File Views und zugehöriger Methoden (app/views/file.py)

* Creation Date : 26-11-2014

* Last Modified : Di 02 Dez 2014 17:47:16 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : -

"""

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
from app.tests.server.viewtestcase import ViewTestCase


class FileTestClass(ViewTestCase):

    # Initialiserung der benötigten Objekte
    # -> wird vor jedem Test ausgeführt
    def setUp(self):
        self.setUpUserAndProjects()
        self.setUpFolders()
        self.setUpFiles()
        self.setUpValues()
        self.setUpHddFiles()


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        #self.tearDownFiles()
        self.tearDownHddFiles()


    # Teste das Erstellen einer neuen leeren .tex Datei
    def test_createtexfile(self):
        # Sende Anfrage zum erstellen einer neuen .tex Datei
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name='newmain.tex')

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        texfileobj = TexFile.objects.get(name='newmain.tex')
        serveranswer = {'id': texfileobj.id, 'name': self._newtex_name1}
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # Sende Anfrage zum erstellen einer neuen .tex Datei mit einem Namen, der bereits im selben Ordner existiert
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1.rootFolder.id,
                                       name='MAIN.tex')

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte ERROR_MESSAGES['FILENAMEEXISTS'] als Fehlermeldung liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENAMEEXISTS'])

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
                                       content=self._new_code1)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # die in der Datenbank gespeicherte .tex Datei sollte als source_code nun den neuen Inhalt besitzen
        self.assertEqual(TexFile.objects.get(id=self._user1_tex1.id).source_code, self._new_code1)

        # Sende Anfrage zum ändern der Datei mit der fileid einer Binärdatei
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_binary1.id,
                                       content=self._new_code1)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOPLAINTEXTFILE'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOPLAINTEXTFILE'])

        # Sende Anfrage zum ändern der Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='updatefile', idpara=self._user2_tex1.id,
                                       content=self._new_code1)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum ändern der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='updatefile', idpara=self._invalidid,
                                       content=self._new_code1)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])

        # Sende Anfrage zum ändern der Datei als user1 mit einer fileid.
        # Die Datei soll nun nur noch einen leeren String beinhalten
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_tex1.id, content='')
        util.validateJsonSuccessResponse(self, response.content, {})


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
        response = util.documentPoster(self, command='deletefile', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    # Teste das umbennen einer Datei
    def test_renamefile(self):
        # Sende Anfrage zum Umbenennen der .tex Datei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex1.id,
                                       name=self._newtex_name1)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.name, self._newtex_name1)

        # Sende Anfrage zum Umbenennen der Binärdatei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_binary1.id,
                                       name=self._newbinary_name1)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        userbinobj = BinaryFile.objects.get(id=self._user1_binary1.id)
        self.assertEqual(userbinobj.name, self._newbinary_name1)

        # Sende Anfrage zum Umbennen einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='renamefile', idpara=self._user2_tex1.id,
                                       name=self._newtex_name1)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum Umbenennen der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='renamefile', idpara=self._invalidid,
                                       name=self._newtex_name1)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])

        # Sende Anfrage zum erstellen einer neuen .tex Datei mit einem Namen, der bereits im selben Ordner existiert
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex2.id,
                                       name=self._user1_tex3.name)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte ERROR_MESSAGES['FILENAMEEXISTS'] als Fehlermeldung liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENAMEEXISTS'])


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
        response = util.documentPoster(self, command='movefile', idpara=self._invalidid,
                                       idpara2=self._user1_project1_folder1.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['FILENOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])

        # Sende Anfrage zum verschieben einer Datei mit einem Namen, der bereits im selben Ziel Ordner existiert
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex3.id,
                                       idpara2=self._user1_project1.rootFolder.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte ERROR_MESSAGES['FILENAMEEXISTS'] als Fehlermeldung liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENAMEEXISTS'])


    # Teste upload lokaler Dateien auf den Server
    def test_uploadfiles(self):
        dic = {
            'command': 'uploadfiles',
            'id': self._user1_project1.rootFolder.id,
            'files': [
                open(self._user1_binfile1_filepath, 'rb'),
                open(self._user1_binfile2_filepath, 'rb'),
                open(self._user1_binfile3_filepath, 'rb')
            ]
        }

        response = self.client.post('/documents/', dic)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte von folgender Form sein:
        dictionary = {'failure': [{'name': '5', 'reason': 'Dateityp ist nicht erlaubt'}],
                      'success': [{'id': 8, 'name': 'test2.tex'}, {'id': 9, 'name': 'test3.jpg'}]
        }

        serveranswer = (util.jsonDecoder(response.content)['response'])

        # Es sollte eig. immer 'success' ausgegeben werden, da auch 'success' kommen sollte, selbst
        # wenn keine einzige Datei akezeptiert wurde
        self.assertEqual(util.jsonDecoder(response.content)['status'], 'success')

        # Es sollten genau 2 Dateien vom Server akzeptiert werden: test2.tex und test3.jpg
        self.assertEqual(len(serveranswer['success']), 2)
        # Eine Datei sollte nicht akzeptiert werden
        self.assertEqual(len(serveranswer['failure']), 1)
        # Der Fehler sollte sein, dass der Dateityp nicht erlaubt ist
        self.assertEqual(serveranswer['failure'][0]['reason'], ERROR_MESSAGES['ILLEGALFILETYPE'])

        # Teste, ob Fehlermeldung, falls versucht wird, Dateien in einen Ordner hochzuladen,
        # auf dem der User keine Rechte hat
        dic['id'] = self._user2_project1_folder1.id
        response = self.client.post('/documents/', dic)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Falls keine Dateien versendet wurden, sollte ebenfalls eine Fehlermeldung zurückgegeben werden
        dic['files'] = None
        dic['id'] = self._user1_project1.rootFolder.id
        response = self.client.post('/documents/', dic)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTALLPOSTPARAMETERS'])


    # Teste download von Dateien auf dem Server zum Client
    def test_downloadfile(self):
        # Sende Anfrage zum Downloaden der test.bin Datei
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_binary1.id)

        # überprüfe die Antwort des Servers
        # der Content-Type sollte 'application/octet-stream' sein
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        # Content-Length sollte (ungefähr) die Größe der originalen Datei besitzen
        ori_file = self._user1_binary1.getContent()
        #self.assertEqual(response['Content-Length'], str(util.getFileSize(ori_file)))
        ori_file.close()
        # Content-Disposition sollte 'attachment; filename=b'test.bin'' sein
        self.assertEqual(response['Content-Disposition'], ('attachment; filename=b\''
                                                           + self._user1_binary1.name + '\''))
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
        # Content-Length sollte (ungefähr) die Größe der originalen Datei besitzen
        ori_file = self._user1_tex1.getContent()
        #self.assertEqual(response['Content-Length'], str(util.getFileSize(ori_file)))
        ori_file.close()
        # Content-Disposition sollte 'attachment; filename=b'test.bin'' sein
        self.assertEqual(response['Content-Disposition'], ('attachment; filename=b\''
                                                           + self._user1_tex1.name + '\''))

        # Sende Anfrage zum Download einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='downloadfile', idpara=self._user2_tex1.id)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)

        # Sende Anfrage zum Download der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='downloadfile', idpara=self._invalidid)

        # überprüfe die Antwort des Servers
        # sollte status code 404 liefern
        self.assertEqual(response.status_code, 404)


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

        self.assertEqual(dictionary['status'], SUCCESS)
        serveranswer = dictionary['response']
        self.assertIn('id', serveranswer)
        self.assertIn('name', serveranswer)

        # Teste Fehlerhafte Datei
        response = util.documentPoster(self, command='compile', idpara=self._user1_tex2.id)
        self.assertContains(response, 'Fatal error occurred, no output PDF file produced!')
