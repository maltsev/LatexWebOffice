"""

* Purpose : Test des Folder Views und zugehöriger Methoden (app/views/folder.py)

* Creation Date : 26-11-2014

* Last Modified : Tu 17 Feb 2015 21:32:00 CET

* Author :  mattis

* Coauthors : christian, ingo

* Sprintnumber : 2

* Backlog entry : -

"""

from app.common.constants import ERROR_MESSAGES
from app.common import util
from app.models.folder import Folder
from app.models.file.file import File
from app.models.collaboration import Collaboration
from app.tests.server.views.viewtestcase import ViewTestCase


class FolderTestClass(ViewTestCase):
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

        pass

    def test_createDir(self):
        """Test der createDir() Methode des folder view

        Teste das Erstellen eines neuen Ordners

        Testfälle:
        - user1 erstellt einen neuen Ordner im rootFolder von project1 -> Erfolg
        - user1 erstellt einen Unterordner in folder1 mit dem selben Namen wie folder1 -> Erfolg
        - user1 erstellt einen weiteren Unterordner in folder1 mit dem selben Namen wie folder1 -> Fehler
        - user1 erstellt einen Unterordner in einem Projekt von user2 -> Fehler
        - user1 erstellt einen neuen Ordner mit einem Namen, der nur Leerzeichen enthält -> Fehler
        - user1 erstellt einen neuen Ordner mit einem Namen, der ein leerer String ist -> Fehler
        - user1 erstellt einen neuen Ordner im rootFolder von user2_sharedproject -> Erfolg

        :return: None
        """

        # Sende Anfrage zum Erstellen eines Ordners im rootfolder von Projekt 1
        response = util.documentPoster(self, command='createdir', idpara=self._user1_project1.rootFolder.id,
                                       name=self._newname1)

        # hole das erstellte Ordner Objekt
        folderobj = Folder.objects.filter(name=self._newname1, parent=self._user1_project1.rootFolder)[0]
        # überprüfe ob der Ordner erstellt wurde
        self.assertTrue(folderobj is not None)
        # Teste, ob der Ordner im richtigen Projekt erstellt wurde
        self.assertEqual(folderobj.getRoot().getProject(), self._user1_project1)

        # erwartete Antwort des Servers
        serveranswer = {
            'id': folderobj.id,
            'name': folderobj.name,
            'parentid': folderobj.parent.id,
            'parentname': folderobj.parent.name
        }

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Erstellen eines neuen Unterordners im Ordner folderobj mit dem selben Namen wie folderobj
        response = util.documentPoster(self, command='createdir', idpara=folderobj.id, name=self._newname1)

        # hole das erstellte Ordner Objekt
        folderobj2 = Folder.objects.filter(name=self._newname1, parent=folderobj)[0]
        # überprüfe ob der Ordner erstellt wurde und der Name richtig gesetzt wurde
        self.assertTrue(folderobj2.name == self._newname1)
        # Teste, ob der Ordner im richtigen Projekt erstellt wurde
        self.assertEqual(folderobj2.getRoot().getProject(), self._user1_project1)

        # erwartete Antwort des Servers
        serveranswer = {
            'id': folderobj2.id,
            'name': self._newname1,
            'parentid': folderobj2.parent.id,
            'parentname': folderobj2.parent.name
        }

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Erstellen eines weiteren Unterordners im Ordner folderobj mit dem selben Namen wie folderobj
        response = util.documentPoster(self, command='createdir', idpara=folderobj.id, name=folderobj.name.upper())

        # Teste, dass das Verzeichnis auch nicht erstellt wurde (es sollte nur ein Ordner mit diesem Namen existieren)
        self.assertTrue(Folder.objects.filter(name=folderobj.name, parent=folderobj).count() == 1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FOLDERNAMEEXISTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Erstellen eines neuen Ordners im RootFolder von user2 (als user1)
        response = util.documentPoster(self, command='createdir', idpara=self._user2_project1.rootFolder.id,
                                       name=self._newname2)

        # Teste, dass das Verzeichnis auch nicht erstellt wurde
        self.assertFalse(Folder.objects.filter(name=self._newname2, parent=self._user2_project1.rootFolder).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Erstellen eines neuen Ordners mit einem Namen, der nur aus Leerzeichen besteht
        response = util.documentPoster(self, command='createdir', idpara=self._user1_project1.rootFolder.id,
                                       name=self._name_only_spaces)

        # Teste, dass das Verzeichnis auch nicht erstellt wurde
        self.assertFalse(Folder.objects.filter(name=self._name_only_spaces,
                                               parent=self._user1_project1.rootFolder).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Erstellen eines neuen Ordners mit einem Namen, der ein leerer String ist
        response = util.documentPoster(self, command='createdir', idpara=self._user1_project1.rootFolder.id,
                                       name=self._name_blank)

        # Teste, dass das Verzeichnis auch nicht erstellt wurde
        self.assertFalse(Folder.objects.filter(name=self._name_blank, parent=self._user1_project1.rootFolder).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)



        response = util.documentPoster(self, command='createdir', idpara=self._user2_sharedproject.rootFolder.id,
                                       name=self._newname1)

        folderobj = Folder.objects.get(name=self._newname1, parent=self._user2_sharedproject.rootFolder)
        self.assertEqual(folderobj.getRoot().getProject(), self._user2_sharedproject)


        serveranswer = {
            'id': folderobj.id,
            'name': folderobj.name,
            'parentid': folderobj.parent.id,
            'parentname': folderobj.parent.name
        }
        util.validateJsonSuccessResponse(self, response.content, serveranswer)




    def test_rmDir(self):
        """Test der rmDir() Methode des folder view

        Teste das Löschen eines Ordners

        Testfälle:
        - user1 löscht einen Ordner eines Projektes -> Erfolg
        - user1 löscht Ordner mit einer folderID welche nicht existiert -> Fehler
        - user1 löscht rootFolder eines Projektes -> Fehler
        - user1 löscht Ordner eines Projektes welches user2 gehört -> Fehler
        - user1 löscht einen Ordner aus user2_sharedproject -> Erfolg
        - user1 löscht einen gesperrten (von user2) Ordner -> Fehler
        - user1 löscht einen gesperrten (von sich selbst) Ordner -> Erfolg

        :return: None
        """

        oldrootfolderid = self._user1_project1.rootFolder.id
        oldtodeletefolder = self._user1_project1_folder2
        oldsubdeletefolder = self._user1_project1_folder2_subfolder1
        oldfileid = self._user1_binary1.id

        # Stelle sicher, dass zu diesem Zeitpunkt der rootordner von project1 noch existiert
        self.assertTrue(Folder.objects.filter(id=oldrootfolderid).exists())
        # Stelle sicher, dass es zu diesem Projekt mind. ein Unterverzeichnis existiert + mind. eine Datei
        self.assertEqual(self._user1_project1_folder1.parent, self._user1_project1.rootFolder)
        self.assertTrue(File.objects.filter(id=oldfileid).exists())

        # Sende Anfrage zum Löschen eines Ordners
        response = util.documentPoster(self, command='rmdir', idpara=self._user1_project1_folder2.id)

        # Ordner sollte nicht mehr in der Datenbank vorhanden sein
        self.assertFalse(Folder.objects.filter(id=oldtodeletefolder.id).exists())
        # Unterverzeichnisse und Dateien sollten dabei auch gelöscht werden!
        self.assertFalse(Folder.objects.filter(id=oldsubdeletefolder.id).exists())
        # Files von Unterverzeichnissen ebenso
        self.assertFalse(File.objects.filter(id=oldfileid).exists())

        # erwartete Antwort des Servers
        serveranswer = {}

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines Ordners mit einer folderID welche nicht existiert
        response = util.documentPoster(self, command='rmdir', idpara=self._invalidid)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['DIRECTORYNOTEXIST']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines RootFolders von einem Projekt
        response = util.documentPoster(self, command='rmdir', idpara=self._user1_project1.rootFolder.id)

        # der rootFolder sollte noch existieren
        self.assertTrue(Folder.objects.filter(id=self._user1_project1.rootFolder.id).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Löschen eines Ordners von einem Projekt welches user2 gehört (als user1)
        response = util.documentPoster(self, command='rmdir', idpara=self._user2_project1_folder1.id)

        # user2_project1_folder1 sollte noch existieren
        self.assertTrue(Folder.objects.filter(id=self._user2_project1_folder1.id).exists())

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)


        # user1 löscht einen Ordner aus user2_sharedproject
        response = util.documentPoster(self, command='rmdir', idpara=self._user2_sharedproject_folder2.id)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(Folder.objects.filter(id=self._user2_sharedproject_folder2.id).exists())


        # user1 löscht einen gesperrten (von user2) Ordner
        self._user2_sharedproject_folder1_texfile.lock(self._user2)
        response = util.documentPoster(self, command='rmdir', idpara=self._user2_sharedproject_folder1.id)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['DIRLOCKED'])
        self.assertTrue(Folder.objects.filter(id=self._user2_sharedproject_folder1.id).exists())


        # user1 löscht einen gesperrten (von sich selbst) Ordner
        self._user2_sharedproject_folder1_texfile.unlock()
        self._user2_sharedproject_folder1_texfile.lock(self._user1)
        response = util.documentPoster(self, command='rmdir', idpara=self._user2_sharedproject_folder1.id)
        util.validateJsonSuccessResponse(self, response.content, {})
        self.assertFalse(Folder.objects.filter(id=self._user2_sharedproject_folder1.id).exists())



    def test_renameDir(self):
        """Test der renameDir() Methode des folder view

        Teste das Umbenennen eines Ordners

        Testfälle:
        - user1 benennt einen Ordner um -> Erfolg
        - user1 benennt einen Ordner um mit einem Namen der bereits im selben Verzeichnis existiert -> Fehler
        - user1 benennt einen Ordner um der user2 gehört -> Fehler
        - user1 benennt einen Ordner um mit einem Namen der nur aus Leerzeichen besteht -> Fehler
        - user1 benennt einen Ordner um mit einem Namen der ein leerer String ist -> Fehler
        - user1 benennt einen Ordner um mit einem Namen der ungültige Zeichen enthält -> Fehler
        - user1 benennt einen Ordner aus user2_sharedproject um -> Erfolg

        :return: None
        """

        oldid = self._user1_project1_folder1.id

        # Sende Anfrage zum Umbenennen eines Ordners
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder1.id,
                                       name=self._newname1)

        # der Ordner sollte in der Datenbank den neuen Namen besitzen
        self.assertEqual(Folder.objects.get(id=self._user1_project1_folder1.id).name, self._newname1)

        # erwartete Antwort des Servers
        serveranswer = {
            'id': self._user1_project1_folder1.id,
            'name': self._newname1
        }

        # überprüfe die Antwort des Servers
        # status sollte success sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenennen eines Ordners mit einem Namen der bereits im selben Verzeichnis existiert
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder2.id,
                                       name=self._newname1)

        # der Name des Ordners sollte nicht zu newname1 geändert worden sein
        self.assertNotEqual(Folder.objects.get(id=self._user1_project1_folder2.id).name, self._newname1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FOLDERNAMEEXISTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenenne eines Ordners von einem Projekt das user2 gehört
        response = util.documentPoster(self, command='renamedir', idpara=self._user2_project1_folder1.id,
                                       name=self._newname2)

        # der Name des Ordners sollte nicht zu newname2 geändert worden sein
        self.assertNotEqual(Folder.objects.get(id=self._user2_project1_folder1.id).name, self._newname2)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenenne eines Ordners mit einem Namen der nur aus Leerzeichen besteht
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder2.id,
                                       name=self._name_only_spaces)

        # der Name des Ordners sollte nicht zu name_only_spaces geändert worden sein
        self.assertNotEqual(Folder.objects.get(id=self._user1_project1_folder2.id).name, self._name_only_spaces)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenenne eines Ordners mit einem Namen der ein leerer String ist
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder2.id,
                                       name=self._name_blank)

        # der Name des Ordners sollte nicht zu name_blank geändert worden sein
        self.assertNotEqual(Folder.objects.get(id=self._user1_project1_folder2.id).name, self._name_blank)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['BLANKNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Umbenenne eines Ordners mit einem Namen der ungültige Sonderzeichen enthält
        response = util.documentPoster(self, command='renamedir', idpara=self._user1_project1_folder2.id,
                                       name=self._name_invalid_chars)

        # der Name des Ordners sollte nicht zu name_invalid_chars geändert worden sein
        self.assertNotEqual(Folder.objects.get(id=self._user1_project1_folder2.id).name, self._name_invalid_chars)

        serveranswer = ERROR_MESSAGES['INVALIDNAME']

        # überprüfe die Antwort des Servers
        # status sollte failure sein
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)


        # user1 benennt einen Ordner aus user2_sharedproject um
        response = util.documentPoster(self, command='renamedir', idpara=self._user2_sharedproject_folder1.id,
                                       name=self._newname1)
        self.assertEqual(Folder.objects.get(pk=self._user2_sharedproject_folder1.id).name, self._newname1)

        serveranswer = {
            'id': self._user2_sharedproject_folder1.id,
            'name': self._newname1
        }
        util.validateJsonSuccessResponse(self, response.content, serveranswer)



    def test_moveDir(self):
        """Test der moveDir() Methode des folder view

        Teste das Verschieben eines Ordners

        Testfälle:
        - user1 verschiebt einen Ordner in einen anderen Ordner -> Erfolg
        - user1 verschiebt einen Ordner zwischen zwei Projekten -> Erfolg
        - user1 verschiebt einen Ordner in einen Ordner der zum einem Projekt von user2 gehört -> Fehler
        - user1 verschiebt einen Ordner welcher zum einem Projekt von user2 gehört -> Fehler
        - user1 verschiebt einen Ordner mit einer folderID die nicht existiert -> Fehler
        - user1 verschiebt einen Ordner wobei die folderID des Zielordners nicht existiert -> Fehler
        - user1 verschiebt einen Ordner wobei im Zielordner bereits ein Ordner mit dem selben Namen existiert -> Fehler
          (dieser Test dient der Überprüfung, ob richtig erkannt wird, dass ein Ordner mit Umlauten im Namen
           bereits mit dem selben Ordner existiert, bsp. Übungs 01 -> übung 01 sollte einen Fehler liefern)
        - user1 verschiebt einen Ordner in einen anderen Ordner aus user2_sharedproject -> Erfolg

        :return: None
        """

        # Sende Anfrage zum verschieben des folder1 in den folder2
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder1.id,
                                       idpara2=self._user1_project1_folder2.id)

        # folder2 sollte nun der neuen parentfolder sein
        self.assertEqual(Folder.objects.get(id=self._user1_project1_folder1.id).parent, self._user1_project1_folder2)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_project1_folder1.id,
                        'name': self._user1_project1_folder1.name,
                        'parentid': self._user1_project1_folder2.id,
                        'parentname': self._user1_project1_folder2.name,
                        'rootid': self._user1_project1_folder1.root.id}

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben von einem Ordner zu einem anderen Projekt
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder2.id,
                                       idpara2=self._user1_project2.rootFolder.id)

        folderobj = Folder.objects.get(id=self._user1_project1_folder2.id)

        # der Ordner sollte nun project2.rootFolder als parent und neuen rootFolder haben
        self.assertEqual(folderobj.parent, self._user1_project2.rootFolder)
        self.assertEqual(folderobj.getRoot(), self._user1_project2.rootFolder)

        # erwartete Antwort des Servers
        serveranswer = {'id': self._user1_project1_folder2.id,
                        'name': self._user1_project1_folder2.name,
                        'parentid': self._user1_project2.rootFolder.id,
                        'parentname': self._user1_project2.rootFolder.name,
                        'rootid': self._user1_project2.rootFolder.id}

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben eines Ordners in einen Ordner der zum einem Projekt von user2 gehört
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder2.id,
                                       idpara2=self._user2_project1.rootFolder.id)

        # der parentFolder sollte nicht user2_project1.rootFolder sein
        self.assertNotEqual(Folder.objects.get(id=self._user1_project1_folder2.id).parent,
                            self._user2_project1.rootFolder)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben eines Ordners der user1 nicht gehört
        response = util.documentPoster(self, command='movedir', idpara=self._user2_project1_folder1.id,
                                       idpara2=self._user1_project1_folder1.id)

        # der parentFolder sollte nicht user1_project1_folder1 sein
        self.assertNotEqual(Folder.objects.get(id=self._user2_project1_folder1.id).parent, self._user1_project1_folder1)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Anzahl der Ordner welche folder2 als parentFolder haben
        old_parent_count = Folder.objects.filter(parent=self._user1_project1_folder2).count()

        # Sende Anfrage zum Verschieben eines Ordners mit einer ungültigen ID
        response = util.documentPoster(self, command='movedir', idpara=self._invalidid,
                                       idpara2=self._user1_project1_folder2.id)

        # es sollte kein weiterer Ordner folder2 nun als parent besitzen
        self.assertEqual(Folder.objects.filter(parent=self._user1_project1_folder2).count(), old_parent_count)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['DIRECTORYNOTEXIST']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Verschieben eines Ordners, wobei im Zielordner bereits ein Ordner mit selben Namen existiert
        # Testet ob die Überprüfung auf Ordner mit dem selben Namen richtig funktioniert, wobei im Namen Umlaute sind
        # wird nur ausgeführt wenn keine SQLITE Datenbank benutzt wird, da dies sonst nicht unterstützt wird
        if not util.isSQLiteDatabse():
            response = util.documentPoster(self, command='movedir', idpara=self._user1_project4_folder3.id,
                                           idpara2=self._user1_project4_folder1.id)

            # der parentFolder sollte nicht user1_project4_folder1 sein
            self.assertNotEqual(Folder.objects.get(id=self._user1_project4_folder3.id).parent,
                                self._user1_project4_folder1)

            # erwartete Antwort des Servers
            serveranswer = ERROR_MESSAGES['FOLDERNAMEEXISTS']

            # überprüfe die Antwort des Servers
            # sollte failure als status liefern
            # response sollte mit serveranswer übereinstimmen
            util.validateJsonFailureResponse(self, response.content, serveranswer)



        response = util.documentPoster(self, command='movedir', idpara=self._user2_sharedproject_folder1.id,
                                       idpara2=self._user2_sharedproject_folder2.id)
        self.assertEqual(Folder.objects.get(pk=self._user2_sharedproject_folder1.id).parent, self._user2_sharedproject_folder2)

        serveranswer = {'id': self._user2_sharedproject_folder1.id,
                        'name': self._user2_sharedproject_folder1.name,
                        'parentid': self._user2_sharedproject_folder2.id,
                        'parentname': self._user2_sharedproject_folder2.name,
                        'rootid': self._user2_sharedproject_folder1.root.id}
        util.validateJsonSuccessResponse(self, response.content, serveranswer)


    def test_moveDir2(self):
        """Test2 der moveDir() Methode des folder view

        Teste das Verschieben eines Ordners

        Testfälle:
        - user1 verschiebt einen Ordner, wobei im Zielordner ein gleichnamiges Verzeichnis existiert -> Fehler

        :return: None
        """

        # Benenne subfolder so um, dass er den gleichen Namen, wie parentfolder
        self._user1_project1_folder2_subfolder1.name = self._user1_project1_folder2.name
        self._user1_project1_folder2_subfolder1.save()

        # Versuche subfolder in den gleichen Ordner wie parentfolder zu verschieben
        response = util.documentPoster(self, command='movedir', idpara=self._user1_project1_folder2_subfolder1.id,
                                       idpara2=self._user1_project1_folder2.parent.id)

        # subfolder1 sollte nicht den selben übergeordnerten Ordner wie folder2 haben
        self.assertNotEqual(Folder.objects.get(id=self._user1_project1_folder2_subfolder1.id).parent,
                            self._user1_project1_folder2.parent)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FOLDERNAMEEXISTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

    def test_listFiles(self):
        """Test der listFiles() Methode des folder view

        Teste das Auflisten der Datei- und Ordnerstruktur eines Ordners.

        Testfälle:
        - user2 listet Dateien und Ordner des project1 auf -> Erfolg
        - user1 listet Dateien und Ordner des project1 auf -> Erfolg
        - user1 listet Dateien und Ordner eines Projektes auf welches user2 gehört -> Fehler
        - user1 listet Dateien und Ordner eines nicht vorhandenen Ordners auf -> Fehler
        - user1 listet Dateien des freigegebenen project2 von user2 (Einladung ist nicht bestätigt) -> Fehler
        - user1 listet Dateien des freigegebenen project2 von user2 (Einladung ist bestätigt) -> Erfold

        :return: None
        """

        # logge user2 ein
        self.client.logout()
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)

        # Sende Anfrage der Datei- und Ordnerstruktur von _user2_project1 (rootFolder)
        # (Aufbau siehe SetUp Methoden in viewtestcase.py)
        response = util.documentPoster(self, command='listfiles', idpara=self._user2_project1.rootFolder.id)

        # hole das rootFolder und maintex Objekt
        rootfolder = self._user2_project1.rootFolder
        maintex = rootfolder.getMainTex()

        # erwartete Antwort des Servers
        serveranswer = {
            'id': rootfolder.id,
            'name': rootfolder.name,
            'project': rootfolder.getProject().name,
            'files': [
                {'id': maintex.id,
                 'name': maintex.name,
                 'mimetype': maintex.mimeType,
                 'size': maintex.size,
                 'createTime': str(maintex.createTime),
                 'lastModifiedTime': str(maintex.lastModifiedTime),
                 'isAllowEdit': not maintex.isLocked()}
            ],
            'folders': [{
                            'id': self._user2_project1_folder1.id,
                            'name': self._user2_project1_folder1.name,
                            'folders': [
                                {'id': self._user2_project1_folder1_subfolder1.id,
                                 'name': self._user2_project1_folder1_subfolder1.name,
                                 'files': [],
                                 'folders': []},
                            ],
                            'files': [],
                        }]
        }

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # logge user1 ein
        self.client.logout()
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

        # Sende Anfrage der Datei- und Ordnerstruktur von _user1_project1 (rootFolder)
        # (Aufbau siehe SetUp Methoden in viewtestcase.py)
        response = util.documentPoster(self, command='listfiles', idpara=self._user1_project1.rootFolder.id)

        # hole das rootFolder und maintex Objekt
        rootfolder = self._user1_project1.rootFolder
        maintex = rootfolder.getMainTex()

        # erwartete Antwort des Servers
        serveranswer = {
            'id': rootfolder.id,
            'name': rootfolder.name,
            'project': rootfolder.getProject().name,
            'files': [
                {'id': maintex.id,
                 'name': maintex.name,
                 'mimetype': maintex.mimeType,
                 'size': maintex.size,
                 'createTime': str(maintex.createTime),
                 'lastModifiedTime': str(maintex.lastModifiedTime),
                 'isAllowEdit': not maintex.isLocked()},
                {'id': self._user1_tex2.id,
                 'name': self._user1_tex2.name,
                 'mimetype': self._user1_tex2.mimeType,
                 'size': self._user1_tex2.size,
                 'createTime': str(self._user1_tex2.createTime),
                 'lastModifiedTime': str(self._user1_tex2.lastModifiedTime),
                 'isAllowEdit': not self._user1_tex2.isLocked()}
            ],
            'folders': [
                {
                    'id': self._user1_project1_folder1.id,
                    'name': self._user1_project1_folder1.name,
                    'folders': [],
                    'files': [
                        {'id': self._user1_tex3.id,
                         'name': self._user1_tex3.name,
                         'mimetype': self._user1_tex3.mimeType,
                         'size': self._user1_tex3.size,
                         'createTime': str(self._user1_tex3.createTime),
                         'lastModifiedTime': str(self._user1_tex3.lastModifiedTime),
                         'isAllowEdit': not self._user1_tex3.isLocked()},
                        {'id': self._user1_tex4.id,
                         'name': self._user1_tex4.name,
                         'mimetype': self._user1_tex4.mimeType,
                         'size': self._user1_tex4.size,
                         'createTime': str(self._user1_tex4.createTime),
                         'lastModifiedTime': str(self._user1_tex4.lastModifiedTime),
                         'isAllowEdit': not self._user1_tex4.isLocked()}
                    ]
                },
                {
                    'id': self._user1_project1_folder2.id,
                    'name': self._user1_project1_folder2.name,
                    'folders': [
                        {'id': self._user1_project1_folder2_subfolder1.id,
                         'name': self._user1_project1_folder2_subfolder1.name,
                         'files': [
                             {'id': self._user1_binary1.id,
                              'name': self._user1_binary1.name,
                              'mimetype': self._user1_binary1.mimeType,
                              'size': self._user1_binary1.size,
                              'createTime': str(self._user1_binary1.createTime),
                              'lastModifiedTime': str(self._user1_binary1.lastModifiedTime),
                              'isAllowEdit': not self._user1_binary1.isLocked()},
                             {'id': self._user1_binary2.id,
                              'name': self._user1_binary2.name,
                              'mimetype': self._user1_binary2.mimeType,
                              'size': self._user1_binary2.size,
                              'createTime': str(self._user1_binary2.createTime),
                              'lastModifiedTime': str(self._user1_binary2.lastModifiedTime),
                              'isAllowEdit': not self._user1_binary2.isLocked()},
                             {'id': self._user1_binary3.id,
                              'name': self._user1_binary3.name,
                              'mimetype': self._user1_binary3.mimeType,
                              'size': self._user1_binary3.size,
                              'createTime': str(self._user1_binary3.createTime),
                              'lastModifiedTime': str(self._user1_binary3.lastModifiedTime),
                              'isAllowEdit': not self._user1_binary3.isLocked()}
                         ],
                         'folders': []},
                    ],
                    'files': [],
                }
            ]
        }

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage der Datei- und Ordnerstruktur von einem Ordner welcher user2 gehört (als user1)
        response = util.documentPoster(self, command='listfiles', idpara=self._user2_project1.rootFolder.id)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage der Datei- und Ordnerstruktur von einem nicht existierenden Ordner
        response = util.documentPoster(self, command='listfiles', idpara=self._invalidid)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['DIRECTORYNOTEXIST']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # response sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)



        collaboration = Collaboration.objects.create(user=self._user1, project=self._user2_project2)
        response = util.documentPoster(self, command='listfiles', idpara=self._user2_project2.rootFolder.id)
        util.validateJsonFailureResponse(self, response.content, ERROR_MESSAGES['NOTENOUGHRIGHTS'])

        collaboration.isConfirmed = True
        collaboration.save()
        response = util.documentPoster(self, command='listfiles', idpara=self._user2_project2.rootFolder.id)

        maintex = self._user2_project2.rootFolder.getMainTex()
        serveranswer = {
            'id': self._user2_project2.rootFolder.id,
            'name': self._user2_project2.rootFolder.name,
            'project': self._user2_project2.name,
            'files': [  {'id': maintex.id,
                         'name': maintex.name,
                         'mimetype': maintex.mimeType,
                         'size': maintex.size,
                         'createTime': str(maintex.createTime),
                         'lastModifiedTime': str(maintex.lastModifiedTime),
                         'isAllowEdit': not maintex.isLocked()}],
            'folders': []
        }
        self.maxDiff = None
        util.validateJsonSuccessResponse(self, response.content, serveranswer)