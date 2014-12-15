"""

* Purpose : Test des File Views und zugehöriger Methoden (app/views/file.py)

* Creation Date : 26-11-2014

* Last Modified : Sa 13 Dez 2014 14:50:08 CET

* Author :  christian

* Coauthors : mattis, ingo

* Sprintnumber : 2

* Backlog entry : -

"""

import mimetypes
import filecmp
import os

from django.utils.encoding import smart_str

from core import settings
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common import util
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


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        # self.tearDownFiles()
        pass


    # Teste das Erstellen einer neuen leeren .tex Datei
    def test_createtexfile(self):
        # Sende Anfrage zum erstellen einer neuen .tex Datei
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1.rootFolder.id,
                                       name=self._newtex_name1)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        texfileobj = TexFile.objects.get(name=self._newtex_name1)
        serveranswer = {'id': texfileobj.id, 'name': self._newtex_name1}
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # Sende Anfrage zum erstellen einer neuen .tex Datei mit einem Namen, der bereits im selben Ordner existiert
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1.rootFolder.id,
                                       name=self._newtex_name1.upper())

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte ERROR_MESSAGES['FILENAMEEXISTS'] als Fehlermeldung liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENAMEEXISTS'])

        # Sende Anfrage zum erstellen der Datei als user1 mit der folderid die user2 gehört
        response = util.documentPoster(self, command='createtex', idpara=self._user2_project1_folder1.id,
                                       name=self._newtex_name2)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['NOTENOUGHRIGHTS'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # Sende Anfrage zum erstellen der Datei als user1 mit einer folderid die nicht existiert
        response = util.documentPoster(self, command='createtex', idpara=100000, name=self._newtex_name2)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte die Fehlermeldung ERROR_MESSAGES['DIRECTORYNOTEXIST'] liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['DIRECTORYNOTEXIST'])

        # Sende Anfrage zum erstellen der Datei als user1 mit einem ungültigen Namen
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name=self._name_invalid_chars)

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
        util.validateJsonSuccessResponse(self, response.content, {'id': self._user1_tex1.id,
                                                                  'name': self._newtex_name1})
        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.name, self._newtex_name1)

        # Sende Anfrage zum Umbenennen der Binärdatei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_binary1.id,
                                       name=self._newbinary_name1)

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte leer sein
        util.validateJsonSuccessResponse(self, response.content, {'id': self._user1_binary1.id,
                                                                  'name': self._newbinary_name1})
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
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._user1_tex4.name.upper())

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte ERROR_MESSAGES['FILENAMEEXISTS'] als Fehlermeldung liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENAMEEXISTS'])


    # Teste das Verschieben einer Datei
    def test_movefile(self):
        # Sende Anfrage zum Verschieben der .tex Datei in den Unterorder folder1 des Projektes
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex1.id,
                                       idpara2=self._user1_project1_folder1.id)

        serveranswer = {'id': self._user1_tex1.id,
                        'name': self._user1_tex1.name,
                        'folderid': self._user1_project1_folder1.id,
                        'foldername': self._user1_project1_folder1.name,
                        'rootid': self._user1_tex1.folder.getRoot().id}

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)


        # die .tex Datei sollte nun in folder 2 sein
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.folder, self._user1_project1_folder1)

        # Sende Anfrage zum Verschieben der Binärdatei in den Unterorder folder2 des Projektes
        response = util.documentPoster(self, command='movefile', idpara=self._user1_binary1.id,
                                       idpara2=self._user1_project1_folder2.id)

        serveranswer = {'id': self._user1_binary1.id,
                        'name': self._user1_binary1.name,
                        'folderid': self._user1_project1_folder2.id,
                        'foldername': self._user1_project1_folder2.name,
                        'rootid': self._user1_binary1.folder.getRoot().id}

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)
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
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex4.id,
                                       idpara2=self._user1_project1.rootFolder.id)

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # sollte ERROR_MESSAGES['FILENAMEEXISTS'] als Fehlermeldung liefern
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENAMEEXISTS'])


    # Teste upload lokaler Dateien auf den Server
    def test_uploadfiles(self):
        file1 = open(os.path.join(settings.TESTFILES_ROOT, 'test_bin.bin'), 'rb')
        file2 = open(os.path.join(settings.TESTFILES_ROOT, 'test_tex_simple.tex'), 'rb')
        file3 = open(os.path.join(settings.TESTFILES_ROOT, 'test_jpg.jpg'), 'rb')

        dic = {
            'command': 'uploadfiles',
            'id': self._user1_project1_folder2.id,
            'files': [file1, file2, file3]
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

        serveranswer = (util.jsonDecoder(response.content)['response'])

        # Es sollte eig. immer 'success' ausgegeben werden, da auch 'success' kommen sollte, selbst wenn keine einzige Datei akezeptiert wurde
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

        file1.close()
        file2.close()
        file3.close()


    # Teste download von Dateien auf dem Server zum Client
    def test_downloadfile(self):
        # Sende Anfrage zum Downloaden der test.bin Datei
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_binary1.id)

        # überprüfe die Antwort des Servers
        # der Content-Type sollte 'application/octet-stream' sein
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        # Content-Length sollte (ungefähr) die Größe der originalen Datei besitzen
        ori_file = self._user1_binary1.getContent()
        self.assertEqual(response['Content-Length'], str(util.getFileSize(ori_file)))

        # Content-Disposition sollte 'attachment; filename='test.bin'' sein
        self.assertEqual(response['Content-Disposition'], ('attachment; filename='
                                                           + self._user1_binary1.name))

        tmp = open(os.path.join(settings.PROJECT_ROOT, 'tmp.tex'), 'a+b')
        tmp.write(response.content)
        file = open(self._user1_binary1.filepath, 'rb')
        # der Inhalt der heruntergeladenen Datei und der Datei auf dem Server sollte übereinstimmen
        self.assertTrue(filecmp.cmp(os.path.join(settings.PROJECT_ROOT, 'tmp.tex'), self._user1_binary1.filepath))
        file.close()
        tmp.close()

        ori_file.close()

        # Sende Anfrage zum Downloaden der main.tex Datei
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_tex1.id)

        # überprüfe die Antwort des Servers
        # der Inhalt der heruntergeladenen Datei und der Datei auf dem Server sollte übereinstimmen
        self.assertEqual(self._user1_tex1.source_code, smart_str(response.content))
        # der Content-Type sollte .tex entsprechen
        self.assertEqual(response['Content-Type'], mimetypes.types_map['.tex'])
        # Content-Length sollte (ungefähr) die Größe der originalen Datei besitzen
        ori_file = self._user1_tex1.getContent()
        self.assertEqual(response['Content-Length'], str(util.getFileSize(ori_file)))
        ori_file.close()

        # Content-Disposition sollte 'attachment; filename=b'test.bin'' sein
        self.assertEqual(response['Content-Disposition'], ('attachment; filename='
                                                           + self._user1_tex1.name))

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

        fileobj = self._user1_binary1  # Die Datei, über die Informationen angefordert wurde
        folderobj = self._user1_binary1.folder  # der Ordner, wo fileobj liegt

        serveranswer = {'fileid': fileobj.id,
                        'filename': fileobj.name,
                        'folderid': folderobj.id,
                        'foldername': folderobj.name,
                        'projectid': folderobj.getProject().id,
                        'projectname': folderobj.getProject().name,
                        'createtime': util.datetimeToString(fileobj.createTime),
                        'lastmodifiedtime': util.datetimeToString(fileobj.lastModifiedTime),
                        'size': fileobj.size,
                        'mimetype': fileobj.mimeType,
                        'ownerid': folderobj.getProject().author.id,
                        'ownername': folderobj.getProject().author.username
        }

        # Die zurückgegebenen Informationen sollten mit fileobj und folderobj übereinstimmen
        self.assertDictEqual(serveranswer, util.jsonDecoder(response.content)['response'])

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
        response = util.documentPoster(self, command='compile', idpara=self._user1_tex4.id)

        dictionary = util.jsonDecoder(response.content)
        self.assertEqual(dictionary['status'], FAILURE)

