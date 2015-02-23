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
import tempfile
import shutil

from django.utils.encoding import smart_str

from core import settings
from app.common.constants import ERROR_MESSAGES
from app.common import util
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.tests.server.views.viewtestcase import ViewTestCase


class FileTestClass(ViewTestCase):
    def setUp(self):
        """Setup Methode für die einzelnen Tests

         Diese Funktion wird vor jeder Testfunktion ausgeführt.
         Damit werden die notwendigen Variablen und Modelle für jeden Test neu initialisiert.
         Die Methoden hierzu befinden sich im ViewTestCase (viewtestcase.py).

        :return: None
        """

        self.setUpUserAndProjects()
        self.setUpFolders()
        self.setUpFiles()
        self.setUpValues()
        self.setUpCollaborations()

    def tearDown(self):
        """Freigabe von nicht mehr notwendigen Ressourcen.

        Diese Funktion wird nach jeder Testfunktion ausgeführt.

        :return: None
        """

        # self.tearDownFiles()
        pass

    def test_createTexFile(self):
        """Test der createTexFile() Methode des file view

        Teste das Erstellen einer neuen .tex Datei.

        Testfälle:
        - user1 erstellt eine neue .tex Datei im rootFolder von project1 -> Erfolg
        - user1 erstellt eine .tex Datei mit einem Namen, der bereits im selben Verzeichnis existiert -> Fehler
        - user1 erstellt eine .tex Datei in einem Ordner der zu einem Projekt von user2 gehört -> Fehler
        - user1 erstellt eine .tex Datei in einem Order der nicht existiert -> Fehler
        - user1 erstellt eine .tex Datei mit einem Namen der nur aus Leerzeichen besteht -> Fehler
        - user1 ersteltt eine .tex Datei mit einem Namen der ein leerer String ist -> Fehler
        - user1 erstellt eine .tex Datei mit einem Namen der ungültige Sonderzeichen beinhaltet -> Fehler
        - user1 erstellt eine .tex Datei mit einem Namen der keine Dateiendung besitzt -> Fehler
        - user1 erstellt eine .tex Datei mit einem Namen der nur die Dateiendung besitzt -> Fehler
        - user1 erstellt eine neue .tex Datei im rootFolder von user2_sharedproject -> Erfolg

        :return: None
        """

        # Sende Anfrage zum erstellen einer neuen .tex Datei
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1.rootFolder.id,
                                       name=self._newtex_name1)

        # überprüfe ob die Texdatei in der Datenbank vorhanden ist
        self.assertTrue(TexFile.objects.filter(name=self._newtex_name1,
                                               folder=self._user1_project1.rootFolder.id).exists())

        # hole das texfile Objekt
        texfileobj = TexFile.objects.get(name=self._newtex_name1, folder=self._user1_project1.rootFolder.id)

        # erwartete Antwort des Servers
        serveranswer = {'id': texfileobj.id,
                        'name': self._newtex_name1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen einer neuen .tex Datei mit einem Namen, der bereits im selben Ordner existiert
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1.rootFolder.id,
                                       name=self._newtex_name1.upper())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENAMEEXISTS']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit der folderid die user2 gehört
        response = util.documentPoster(self, command='createtex', idpara=self._user2_project1_folder1.id,
                                       name=self._newtex_name2)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit einer folderid die nicht existiert
        response = util.documentPoster(self, command='createtex', idpara=self._invalidid, name=self._newtex_name2)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['DIRECTORYNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit einem Namen der nur aus Leerzeichen besteht
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name=self._name_only_spaces)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit einem Namen der ein leerer String ist
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name=self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit einem ungültigen Namen
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name=self._name_invalid_chars)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit einem ungültigen Namen (ohne Dateiendung)
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name=self._name_no_ext)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum erstellen der Datei als user1 mit einem ungültigen Namen (nur Dateiendung)
        response = util.documentPoster(self, command='createtex', idpara=self._user1_project1_folder1.id,
                                       name=self._newtex_name_only_ext)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)


        # user1 ist ein Kollaborator von self._user2_sharedproject
        response = util.documentPoster(self, command='createtex', idpara=self._user2_sharedproject.rootFolder.id,
                                       name=self._newtex_name1)

        # überprüfe ob die Texdatei in der Datenbank vorhanden ist
        self.assertTrue(TexFile.objects.filter(name=self._newtex_name1,
                                               folder=self._user2_sharedproject.rootFolder.id).exists())

        # hole das texfile Objekt
        texfileobj = TexFile.objects.get(name=self._newtex_name1, folder=self._user2_sharedproject.rootFolder.id)

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, {'id': texfileobj.id,
                                                                  'name': self._newtex_name1})





    def test_updateFile(self):
        """Test der updateFile() Methode des file view

        Teste das aktualisieren des Inhalts eine PlainTextFile
        (source_code wurde aktualisiert)

        Testfälle:
        - user1 ändert den source code der tex1 datei -> Erfolg
        - user1 ändert den source code der tex1 datei zu einem leeren String -> Erfolg
        - user1 ändert den source code einer Binärdatei -> Fehler
        - user1 ändert den source code einer Datei die user2 gehört -> Fehler
        - user1 ändert den source code einer Datei die nicht existiert -> Fehler
        - user1 ändert den source code der main.tex Datei aus dem user2_sharedproject -> Erfolg

        :return: None
        """

        # Sende Anfrage zum ändern der Datei
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_tex1.id,
                                       content=self._new_code1)

        # die in der Datenbank gespeicherte .tex Datei sollte als source_code nun den neuen Inhalt besitzen
        self.assertEqual(TexFile.objects.get(id=self._user1_tex1.id).source_code, self._new_code1)

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum ändern der Datei als user1 mit einer gültigen fileid.
        # Die Datei soll nun nur noch einen leeren String beinhalten
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_tex1.id, content=self._name_blank)

        # die in der Datenbank gespeicherte .tex Datei sollte als source_code nun den neuen Inhalt besitzen
        self.assertEqual(TexFile.objects.get(id=self._user1_tex1.id).source_code, self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum ändern der Datei mit der fileid einer Binärdatei
        response = util.documentPoster(self, command='updatefile', idpara=self._user1_binary1.id,
                                       content=self._new_code1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOPLAINTEXTFILE']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum ändern der Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='updatefile', idpara=self._user2_tex1.id,
                                       content=self._new_code1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum ändern der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='updatefile', idpara=self._invalidid,
                                       content=self._new_code1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)



        sharedproject_maintex = self._user2_sharedproject.rootFolder.getMainTex()
        response = util.documentPoster(self, command='updatefile', idpara=sharedproject_maintex.id,
                                       content=self._new_code1)

        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertEqual(TexFile.objects.get(id=sharedproject_maintex.id).source_code, self._new_code1)



    def test_deletefile(self):
        """Test der deleteFile() Methode des file view

        Teste das Löschen einer Datei.

        Testfälle:
        - user1 löscht eine vorhandene .tex Datei -> Erfolg
        - user1 löscht eine vorhandene Binärdatei -> Erfolg
        - user1 löscht eine .tex Datei welche user2 gehört -> Fehler
        - user1 löscht eine Datei die nicht existiert -> Fehler
        - user1 löscht die main.tex Datei aus dem user2_sharedproject -> Erfolg
        :return: None
        """

        # Sende Anfrage zum Löschen der .tex Datei
        response = util.documentPoster(self, command='deletefile', idpara=self._user1_tex1.id)

        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        self.assertFalse(PlainTextFile.objects.filter(id=self._user1_tex1.id).exists())

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen der Binärdatei
        response = util.documentPoster(self, command='deletefile', idpara=self._user1_binary1.id)

        # in der Datenbank sollte die Datei nun nicht mehr vorhanden sein
        self.assertFalse(BinaryFile.objects.filter(id=self._user1_binary1.id).exists())

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='deletefile', idpara=self._user2_tex1.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='deletefile', idpara=self._invalidid)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)


        sharedproject_maintex = self._user2_sharedproject.rootFolder.getMainTex()
        response = util.documentPoster(self, command='deletefile', idpara=sharedproject_maintex.id)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(PlainTextFile.objects.filter(id=sharedproject_maintex.id).exists())




    def test_renameFile(self):
        """Test der renameFile() Methode des file view

        Teste das Umbenennen einer Datei.

        Testfälle:
        - user1 benennt eine .tex Datei um -> Erfolg
        - user1 benennt eine Binärdatei um -> Erfolg
        - user1 benennt eine .tex Datei um welche user2 gehört -> Fehler
        - user1 benennt eine Datei um die nicht existiert -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der bereits im selben Ordner existiert -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der nur aus Leerzeichen besteht -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der ein leerer String ist -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der ungültige Sonderzeichen enthält -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der keine Dateiendung besitzt -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der nur aus der Dateiendung besteht -> Fehler
        - user1 benennt eine .tex Datei um mit einem Namen der bereits im selben Ordner existiert -> Fehler
          (dieser Test dient der Überprüfung, ob richtig erkannt wird, dass eine Datei mit Umlauten im Namen
           bereits mit dem selben Ordner existiert, bsp. Übungsblatt 01.tex -> übungsblatt 01.tex sollte einen Fehler
           liefern)
        - user1 benennt die main.tex Datei aus dem user2_sharedproject -> Erfolg

        :return: None
        """

        # Sende Anfrage zum Umbenennen der .tex Datei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex1.id,
                                       name=self._newtex_name1)

        # in der Datenbank sollte die Datei nun den neuen Namen besitzen
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.name, self._newtex_name1)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_tex1.id,
                        'name': self._newtex_name1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen der Binärdatei
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_binary1.id,
                                       name=self._newbinary_name1)

        # in der Datenbank sollte die Datei nun den neuen Namen besitzen
        userbinobj = BinaryFile.objects.get(id=self._user1_binary1.id)
        self.assertEqual(userbinobj.name, self._newbinary_name1)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_binary1.id,
                        'name': self._newbinary_name1}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbennen einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='renamefile', idpara=self._user2_tex1.id,
                                       name=self._newtex_name1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='renamefile', idpara=self._invalidid,
                                       name=self._newtex_name1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der bereits im selben Ordner existiert
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._user1_tex4.name.upper())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENAMEEXISTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der nur aus Leerzeichen besteht
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._name_only_spaces)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der ein leerer String ist
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._name_invalid_chars)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der keine Dateiendung enthält
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._name_no_ext)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der nur die Dateiendung enthält
        response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex3.id,
                                       name=self._newtex_name_only_ext)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen einer .tex Datei mit einem Namen, der bereits im selben Ordner existiert
        # (Überprüfung ob erkannt wird dass diese Datei bereits existiert, wenn sie Umlaute im Namen hat)
        # wird nur ausgeführt wenn keine SQLITE Datenbank benutzt wird, da dies sonst nicht unterstützt wird
        if not util.isSQLiteDatabse():
            response = util.documentPoster(self, command='renamefile', idpara=self._user1_tex5.id,
                                           name=self._newtex_name_specialchars1)

            # erwartete Antwort des Servers
            serveranswer = ERROR_MESSAGES['FILENAMEEXISTS']

            # überprüfe die Antwort des Servers
            # status sollte failure sein
            # die Antwort des Servers sollte mit serveranswer übereinstimmen
            util.validateJsonFailureResponse(self, response.content, serveranswer)


        sharedproject_maintex = self._user2_sharedproject.rootFolder.getMainTex()
        response = util.documentPoster(self, command='renamefile', idpara=sharedproject_maintex.id,
                                       name=self._newtex_name1)
        usertexobj = PlainTextFile.objects.get(id=sharedproject_maintex.id)
        self.assertEqual(usertexobj.name, self._newtex_name1)
        util.validateJsonSuccessResponse(self, response.content, {'id': sharedproject_maintex.id,
                                                                  'name': self._newtex_name1})


    def test_moveFile(self):
        """Test der moveFile() Methode des file view

        Teste das Verschieben einer Datei.

        Testfälle:
        - user1 verschiebt eine .tex Datei in den Unterordner folder1 -> Erfolg
        - user1 verschiebt eine Binärdatei in den Unterordner folder2 -> Erfolg
        - user1 verschiebt eine .tex Datei die user2 gehört -> Fehler
        - user1 verschiebt eine .tex Datei in einen Ordner der user2 gehört -> Fehler
        - user1 verschiebt eine .tex Datei die nicht existiert -> Fehler
        - user1 verschiebt eine .tex Datei mit einem Namen der bereits im Zielordner existiert -> Fehler

        :return: None
        """

        # Sende Anfrage zum Verschieben der .tex Datei in den Unterorder folder1 des Projektes
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex1.id,
                                       idpara2=self._user1_project1_folder1.id)

        # die .tex Datei sollte nun in folder 2 sein
        usertexobj = PlainTextFile.objects.get(id=self._user1_tex1.id)
        self.assertEqual(usertexobj.folder, self._user1_project1_folder1)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_tex1.id,
                        'name': self._user1_tex1.name,
                        'folderid': self._user1_project1_folder1.id,
                        'foldername': self._user1_project1_folder1.name,
                        'rootid': self._user1_tex1.folder.getRoot().id}

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben der Binärdatei in den Unterorder folder2 des Projektes
        response = util.documentPoster(self, command='movefile', idpara=self._user1_binary1.id,
                                       idpara2=self._user1_project1_folder2.id)

        # die Binärdatei sollte nun in folder 2 sein
        userbinobj = BinaryFile.objects.get(id=self._user1_binary1.id)
        self.assertEqual(userbinobj.folder, self._user1_project1_folder2)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_binary1.id,
                        'name': self._user1_binary1.name,
                        'folderid': self._user1_project1_folder2.id,
                        'foldername': self._user1_project1_folder2.name,
                        'rootid': self._user1_binary1.folder.getRoot().id}

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='movefile', idpara=self._user2_tex1.id,
                                       idpara2=self._user1_project1_folder1.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben einer Datei als user1 mit einer folderid die user2 gehört
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex2.id,
                                       idpara2=self._user2_project1_folder1.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='movefile', idpara=self._invalidid,
                                       idpara2=self._user1_project1_folder1.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENOTEXIST']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum verschieben einer Datei mit einem Namen, der bereits im selben Ziel Ordner existiert
        response = util.documentPoster(self, command='movefile', idpara=self._user1_tex4.id,
                                       idpara2=self._user1_project1.rootFolder.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENAMEEXISTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_uploadfiles(self):
        """Test der uploadFiles() Methode des file view

        Teste das Hochladen von Dateien.

        Testfälle:
        - user1 lädt 3 Dateien gleichzeitig hoch -> Erfolg (test_bin.bin sollte jedoch nicht akzeptiert werden)
        - user1 lädt 3 Dateien in einen Ordner von user2 hoch -> Fehler
        - user1 schickt Anfrage ohne Dateien -> Fehler

        :return: None
        """

        # lade die Testdateien für den Upload
        file1_name = 'test_bin.bin'
        file2_name = 'test_tex_simple.tex'
        file3_name = 'test_jpg.jpg'
        file1 = open(os.path.join(settings.TESTFILES_ROOT, file1_name), 'rb')
        file2 = open(os.path.join(settings.TESTFILES_ROOT, file2_name), 'rb')
        file3 = open(os.path.join(settings.TESTFILES_ROOT, file3_name), 'rb')

        # Anfrage an den Server
        serverrequest = {
            'command': 'uploadfiles',
            'id': self._user1_project1_folder2.id,
            'files': [file1, file2, file3]
        }

        # Sende Anfrage an den Server die Dateien hochzuladen
        response = self.client.post('/documents/', serverrequest)

        file1obj = File.objects.filter(name=file1_name, folder=self._user1_project1_folder2)
        self.assertFalse(file1obj.exists())

        file2obj = File.objects.filter(name=file2_name, folder=self._user1_project1_folder2)
        self.assertTrue(file2obj.exists())

        file3obj = File.objects.filter(name=file3_name, folder=self._user1_project1_folder2)
        self.assertTrue(file3obj.exists())


        # erwartete Antwort des Servers
        serveranswer = {
            'failure':
                [
                    {'name': file1_name, 'reason': ERROR_MESSAGES['ILLEGALFILETYPE'].format("application/octet-stream")},
                ],
            'success':
                [
                    {'id': file2obj[0].id, 'name': file2_name},
                    {'id': file3obj[0].id, 'name': file3_name}
                ]
        }

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage an den Server Dateien hochzuladen mit einer folderid die user2 gehört (als user1)
        serverrequest = {
            'command': 'uploadfiles',
            'id': self._user2_project1_folder1.id,
            'files': [file2, file3]
        }

        # Sende Anfrage an den Server die Dateien hochzuladen
        response = self.client.post('/documents/', serverrequest)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage an den Server Dateien hochzuladen ohne Dateien mitzusenden
        serverrequest = {
            'command': 'uploadfiles',
            'id': self._user1_project1.rootFolder.id,
            'files': None
        }

        # Sende Anfrage an den Server die Dateien hochzuladen
        response = self.client.post('/documents/', serverrequest)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTALLPOSTPARAMETERS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # schließe alle geöffneten Testdateien
        file1.close()
        file2.close()
        file3.close()

    def test_downloadFile(self):
        """Test der downloadFile() Methode des file view

        Teste das Hochladen von Dateien.

        Testfälle:
        - user1 lädt eine Binärdatei herunter -> Erfolg
        - user1 lädt eine .tex Datei herunter -> Erfolg
        - user1 lädt eine .tex Datei herunter welche user2 gehört -> Fehler
        - user1 lädt eine Datei herunter die nicht existiert -> Fehler

        :return: None
        """

        # Sende Anfrage zum Downloaden der test.bin Datei
        response = util.documentPoster(self, command='downloadfile', idpara=self._user1_binary1.id)

        # überprüfe die Antwort des Servers
        # der Content-Type sollte 'application/octet-stream' sein
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        # Content-Length sollte (ungefähr) die Größe der originalen Datei besitzen
        file_content = self._user1_binary1.getContent()
        self.assertEqual(response['Content-Length'], str(util.getFileSize(file_content)))

        # Content-Disposition sollte 'attachment; filename='test_bin.bin'' sein
        self.assertEqual(response['Content-Disposition'], ('attachment; filename=\"' + self._user1_binary1.name) + '\"')

        # erstelle ein temporäres Verzeichnis um den filestream als Datei zu speichern
        tmp_dir = tempfile.mkdtemp()
        tmp_file_path = os.path.join(tmp_dir, self._user1_binary1.name)
        tmp_file = open(tmp_file_path, 'a+b')
        tmp_file.write(response.content)

        # öffne die Datei auf dem Server
        ori_file = open(self._user1_binary1.filepath, 'rb')
        # der Inhalt der heruntergeladenen Datei und der Datei auf dem Server sollte übereinstimmen
        self.assertTrue(filecmp.cmp(tmp_file_path, self._user1_binary1.filepath))

        # schließe alle geöffneten Dateien
        ori_file.close()
        tmp_file.close()
        file_content.close()

        # löschen den erstellten temporären Ordner
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

        # --------------------------------------------------------------------------------------------------------------
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

        # Content-Disposition sollte 'attachment; filename='test_bin.bin'' sein
        self.assertEqual(response['Content-Disposition'], ('attachment; filename=\"' + self._user1_tex1.name + '\"'))

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Download einer Datei als user1 mit der fileid einer .tex Datei die user2 gehört
        response = util.documentPoster(self, command='downloadfile', idpara=self._user2_tex1.id)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Download der Datei als user1 mit einer fileid
        # die auf dem Server in der Datenbank nicht existiert
        response = util.documentPoster(self, command='downloadfile', idpara=self._invalidid)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['FILENOTEXIST'])


    def test_fileInfo(self):
        """Test der fileInfo() Methode des file view

        Teste das Anfordern von Informationen zu einer bestimmten Datei,

        Testfälle:
        - user1 fordert Informationen zu einer Binärdatei an -> Erfolg
        - user1 fordert Informationen zu einer .tex Datei an -> Erfolg
        - user1 fordert Informationen zu einer Datei an die nicht existiert -> Fehler
        - user1 fordert Informationen zu einer Datei an welche user2 gehört -> Fehler

        :return: None
        """

        # Sende Anfrage zu Dateiinformation einer Binärdatei
        response = util.documentPoster(self, command='fileinfo', idpara=self._user1_binary1.id)

        # hole die Datei- und Ordnerobjekte
        fileobj = self._user1_binary1
        folderobj = self._user1_binary1.folder
        # ermittelt das Projekt der Datei
        projectobj = folderobj.getProject()

        # erwartete Antwort des Servers
        serveranswer = {
            'fileid': fileobj.id,
            'filename': fileobj.name,
            'folderid': folderobj.id,
            'foldername': folderobj.name,
            'projectid': projectobj.id,
            'projectname': projectobj.name,
            'createtime': util.datetimeToString(fileobj.createTime),
            'lastmodifiedtime': util.datetimeToString(fileobj.lastModifiedTime),
            'size': fileobj.size,
            'mimetype': fileobj.mimeType,
            'ownerid': projectobj.author.id,
            'ownername': projectobj.author.username
        }

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zu Dateiinformation einer .tex Datei
        response = util.documentPoster(self, command='fileinfo', idpara=self._user1_tex2.id)

        # hole die Datei- und Ordnerobjekte
        fileobj = self._user1_tex2
        folderobj = self._user1_tex2.folder
        # ermittelt das Projekt der Datei
        projectobj = folderobj.getProject()

        # erwartete Antwort des Servers
        serveranswer = {
            'fileid': fileobj.id,
            'filename': fileobj.name,
            'folderid': folderobj.id,
            'foldername': folderobj.name,
            'projectid': projectobj.id,
            'projectname': projectobj.name,
            'createtime': util.datetimeToString(fileobj.createTime),
            'lastmodifiedtime': util.datetimeToString(fileobj.lastModifiedTime),
            'size': fileobj.size,
            'mimetype': fileobj.mimeType,
            'ownerid': projectobj.author.id,
            'ownername': projectobj.author.username
        }

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zu Dateiinformation einer Datei die nicht existiert
        response = util.documentPoster(self, command='fileinfo', idpara=self._invalidid)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENOTEXIST']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zu Dateiinformation einer Datei von user2 (als user1)
        response = util.documentPoster(self, command='fileinfo', idpara=self._user2_tex1.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)