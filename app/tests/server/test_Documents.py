"""

* Purpose : Test der Dokument- und Projektverwaltung (app/view/documents.py)

* Creation Date : 20-11-2014

* Last Modified : Di 25 Nov 2014 17:33:33 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry :

"""

from django.test import TestCase,Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from app.common.util import jsonDecoder
from app.models.project import Project
from app.models.folder import Folder
from app.models.file.texfile import TexFile
from app.models.file.file import File
from core.settings import FILEDATA_URL, TMP_FILEDATA_URL
from django.utils.encoding import smart_str
import json, os

@override_settings(FILEDATA_URL=os.path.join(os.path.expanduser('~'), 'latexweboffice', 'tests'),
                   TMP_FILEDATA_URL=os.path.join(FILEDATA_URL, 'tmp'))
class DocumentsTestClass(TestCase):
    def setUp(self):

        # erstelle user1
        self._user1 = User.objects.create_user(
            username='user1@test.de', password='123456')
        self._user1._unhashedpw = '123456'

        # erstelle user2
        self._user2 = User.objects.create_user(
            'user2@test.de', password='test123')
        self._user2._unhashedpw = 'test123'

        # erstelle user3
        self._user3 = User.objects.create_user(
            'user3@test.de', password='test1234')
        self._user3._unhashedpw = 'test1234'
        self.client=Client()

        # logge user1 ein
        self.client.login(username=self._user1.username, password=self._user1._unhashedpw)

        # erstelle die root Ordner für die einzelnen Projekte
        user1_project1_root = Folder(name='user1_project1')
        user1_project1_root.save()
        user1_project2_root = Folder(name='user1_project2')
        user1_project2_root.save()
        user2_project1_root = Folder(name='user2_project1')
        user2_project1_root.save()
        user2_project2_root = Folder(name='user2_project2')
        user2_project2_root.save()

        # erstelle zwei Projekte als user1
        self._user1_project1 = Project.objects.create(name='user1_project1', author=self._user1,
                                                      rootFolder=user1_project1_root)
        self._user1_project1.save()
        self._user1_project2 = Project.objects.create(name='user1_project2', author=self._user1,
                                                      rootFolder=user1_project2_root)
        self._user1_project2.save()

        # erstelle zwei Projekte als user2
        self._user2_project1 = Project.objects.create(name='user2_project1', author=self._user2,
                                                      rootFolder=user2_project1_root)
        self._user2_project1.save()
        self._user2_project2 = Project.objects.create(name='user2_project2', author=self._user2,
                                                      rootFolder=user2_project2_root)
        self._user2_project2.save()


        # Speichere einen Unterordner in das Projekt1 vom User 2
        subfolder=self._user2_project1_subfolder=Folder.objects.create(name='subfolder',root=user2_project1_root,parent=user2_project1_root)
        subfolder.save()
        
        # Speichere ein Dokument in dem Unterordner
        f=TexFile.objects.create(name='main.tex',folder=subfolder,source_code='')
        f.save()
        self._user2_subroot_file=f

    def tearDown(self):
        self.client.logout()

    
    #Helper Methode um leichter die verschiedenen commands durchzutesten.
    def documentPoster(self,command='NoCommand',idpara=None,content=None,name=None,files=None):
        dictionary={'command':command}
        if idpara:
            dictionary['id']=idpara
        if content:
            dictionary['content']=content
        if name:
            dictionary['name']=name
        if files:
            pass #TODO
        return self.client.post('/documents/',dictionary)


    #Teste die Verteilfunktion, die die verschiedenen Document-commands der richtigen Methode zuweist
    def test_Execute(self):

        
        #Teste ungenügend Parameter
        response=self.documentPoster(command='createdir')
        dictionary=jsonDecoder(response.content)
        self.assertEqual(dictionary['status'],FAILURE)

        
        #Teste unbekannten command

        dictionary=jsonDecoder(self.documentPoster(command='DOESNOTEXIST').content)
        self.assertEquals(dictionary['status'],FAILURE)

        
        #Teste Fehlerhafte Parameter:
        #id!=int

        
        #content!=string
        
        
        #name!=string
        
        
        #files!=files
        #TODO
        pass


    #Teste das Erzeugen von Ordnern
    def test_createDir(self):
        response=self.documentPoster(command='createdir',idpara=self._user1_project1.id,name='testFolder')
        dictionary=jsonDecoder(response.content)
        #Teste, ob beim richtiger Anfrage eine Erfolgsmeldung zurückgegeben wird
        self.assertEqual(dictionary['status'],SUCCESS)

        serveranswer=dictionary['response']

        self.assertIn('id',serveranswer)
        self.assertIn('name',serveranswer)
        self.assertIn('parentfolderid',serveranswer)
        self.assertIn('parentfoldername', serveranswer)

        self.assertTrue(serveranswer['name'],'testFolder')

        #Teste, ob der Ordner wirklich existiert und mit dem Werten, die zurückgegeben wurden, übereinstimmt
        self.assertTrue(Folder.objects.filter(id=serveranswer['id']).exists())
        self.assertTrue(Folder.objects.filter(name='testFolder').exists())
        folder1=Folder.objects.get(id=serveranswer['id'])
        #Teste, ob der Ordner im richtigen Projekt erstellt wurde 
        self.assertEqual(folder1.getRoot().getProject(),self._user1_project1)
        
        #Teste, ob ein Unterverzeichnis von einem Unterverzeichnis angelegt werden kann und das auch mit dem gleichen Namen
        response=self.documentPoster(command='createdir',idpara=folder1.id,name='root')
        dictionary=jsonDecoder(response.content)
        self.assertTrue(Folder.objects.filter(id=dictionary['response']['id']).exists())
        #Teste, ob ein Verzeichnis zwei gleichnamige Unterverzeichnisse haben kann
        response=self.documentPoster(command='createdir',idpara=folder1.id,name='root')
        dictionary=jsonDecoder(response.content)
        #TODO #############################################################
        #self.assertEqual(dictionary['response'],ERROR_MESSAGES['FOLDERNAMEEXISTS'])
        #SOLLTE DATENBANK MACHEN ##########################################

        #Teste, wie es sich mit falschen Angaben verhält

        #Teste ob user1 in einem Project vom user2 ein Verzeichnis erstellen kann
        response=self.documentPoster(command='createdir',idpara=self._user2_project1.id,name='IDONOTEXISTDIR')
        dictionary=jsonDecoder(response.content)
        self.assertEqual(dictionary['status'],FAILURE)
        #Teste, dass die richtige Fehlermeldung zurückgegeben wird
        dictionaryresponse=dictionary['response']
        self.assertEqual(dictionaryresponse,ERROR_MESSAGES['NOTENOUGHRIGHTS'])
        #Teste, dass das Verzeichnis auch nicht erstellt wurde
        self.assertFalse(Folder.objects.filter(name='IDONOTEXISTDIR').exists())

        #Teste auf leeren Verzeichnisnamen
        response=self.documentPoster(command='createdir',idpara=self._user1_project1.id,name=' ')
        dictionary=jsonDecoder(response.content)
        serveranswer=dictionary['response']
        self.assertEqual(serveranswer,ERROR_MESSAGES['BLANKNAME'])

    
    #Teste das Unbenennen von Ordnern
    def test_renameDir(self):
        oldid=self._user1_project1.id
        response=self.documentPoster(command='renamedir', idpara=self._user1_project1.id,name='New project und directory name')

        dictionary=jsonDecoder(response.content)
        serveranswer=dictionary['response']
        
        #Teste auf richtige Response Daten bei einer Anfrage, die funktionieren sollte
        self.assertEqual(dictionary['status'],SUCCESS)

        self.assertIn('id',serveranswer)
        self.assertIn('name',serveranswer)

        self.assertEqual(serveranswer['id'],oldid)
        self.assertEqual(serveranswer['name'],'New project und directory name')


        #Teste, ob ein anderer User das Projekt eines anderen unbenennen kann
        response=self.documentPoster(command='renamedir',idpara=self._user2_project1.id,name='ROFL')
        dictionary=jsonDecoder(response.content)
        serveranswer=dictionary['response']

        self.assertEqual(dictionary['status'],FAILURE)
        
        self.assertEqual(ERROR_MESSAGES['NOTENOUGHRIGHTS'],serveranswer)




    #Teste, ob ein Unterverzeichnis den gleichen Namen haben kann, wie ein anderes Unterverzeichnis im gleichen Elternverzeichnis: Überflüssig, da dies bereits schon in test_createDir getestet wird
    
    #Teste, ob ein Verzeichnis einen leeren Namen haben kann: Überflüssig, da dies bereits schon in der test_createDir Methode getestet wird
       

    #Teste das Löschen eines Ordners
    #Teste, ob Unterordner und zum Ordner gehörende Dateien auch gelöscht werden
    def test_rmDir(self):

        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)
        oldid=self._user2_project1.id
        oldfileid=self._user2_subroot_file.id
        #Stelle sicher, dass zu diesem Zeitpunkt project2 noch existiert 
        self.assertTrue(Project.objects.filter(id=oldid).exists())
        #Stelle sicher, dass es zu diesem Projekt mind. ein Unterverzeichnis existiert + mind. eine Datei
        self.assertEqual(self._user2_project1_subfolder.parent,self._user2_project1.rootFolder)
        self.assertTrue(TexFile.objects.filter(id=oldfileid).exists())
        
        response=self.documentPoster(command='rmdir',idpara=self._user2_project1.id)
        dictionary=jsonDecoder(response.content)
        serveranswer=dictionary['response']

        self.assertEqual(dictionary['status'],SUCCESS)
        
        #Das Projekt sollte komplett gelöscht worden sein
        self.assertFalse(Project.objects.filter(id=oldid).exists())
        #Unterverzeichnisse und Dateien sollten dabei auch gelöscht werden! (klappt nocht nicht)
        #TODO self.assertFalse(Folder.objects.filter(id=self._user2_project1_subfolder).exists())
        #Files von Unterverzeichnissen ebenso
        #TODO self.assertFalse(Document.objects.filter(id=oldfileid).exists())

    
    #Teste das Abrufen von Informationen einer Datei via fileid
    def WaitingForNewDatabaseModelstest_fileInfo(self):
        response=self.documentPoster(command='fileinfo',idpara=self._user2_subroot_file)
        dictioanry=jsonDecoder(response.content)
        serveranswer=dictioanry['response']

        self.assertEqual(dictioanry['status'],SUCCESS)

        #Es sollten richtige Informationen zur Datei zurückgegeben worden sein
        self.assertIn('fileid',serveranswer)
        self.assertIn('filename',serveranswer)
        self.assertIn('folderid',serveranswer)
        self.assertIn('foldername',serveranswer)

        fileobj=self._user2_subroot_file # Die Datei, über die Informationen angefordert wurde
        folder=self._user2_project1_subfolder #der Ordner, wo fileobj liegt
        
        #Die zurückgegebenen Informationen sollten mit fileobj und folder übereinstimmen
        self.assertEqual(serveranswer['fileid'],fileobj.id)
        self.assertEqual(serveranswer['filename'],fileobj.name)
        self.assertEqual(serveranswer['folderid'],folder.id)
        self.assertEqual(serveranswer['foldername'],folder.name)



        #self.assertEqual(serveranswer['fileid'],



    # Teste Erstellen eines Projektes:
    # - ein Benutzer erstellt zwei neue Projekte -> success
    # - ein Benutzer erstellt ein weiteres Projekt, wobei der Projektname nur aus Leerzeichen besteht -> Fehlermeldung
    # - ein Benutzer erstellt ein weiteres Projekt, wobei der Projektname bereits existiert -> Fehlermeldung
    def test_projectCreate(self):
        # rufe die URL mit den entsprechenden Parametern zum Erstellen eines Projektes auf
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project3'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)
        # teste ob id vorhanden ist
        self.assertIn('id', dictionary['response'])
        # teste ob name vorhanden ist
        self.assertIn('name', dictionary['response'])
        # teste ob name mit dem übergebenen Projektnamen übereinstimmt
        self.assertEqual(dictionary['response']['name'], 'user1_project3')

        # id vom Projekt 3 von user1
        user1_project3_id = dictionary['response']['id']

        # erzeuge ein weiteres Projekt
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project4'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # id vom Projekt 4 von user1
        user1_project4_id = dictionary['response']['id']

        # überprüfe, ob die erstellten Projekte in der Datenbank vorhanden sind
        # user1_project3
        self.assertTrue(Project.objects.get(id=user1_project3_id))
        # überprüfe ob für dieses Projekt der root Ordner in der Datenbank angelegt wurde
        self.assertTrue(Project.objects.get(id=user1_project3_id).rootFolder)
        # TODO
        # überprüfe ob die main.tex Datei in der Datenbank vorhanden ist
        # user1_project4
        self.assertTrue(Project.objects.get(id=user1_project4_id))
        # überprüfe ob für dieses Projekt der root Ordner in der Datenbank angelegt wurde
        self.assertTrue(Project.objects.get(id=user1_project4_id).rootFolder)
        # TODO
        # überprüfe ob die main.tex Datei in der Datenbank vorhanden ist

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein Projekt, dessen Name nur aus Leerzeichen besteht
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': '    '})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['PROJECTNAMEONLYWHITESPACE'])

        # --------------------------------------------------------------------------------------------------------------
        # erzeuge ein weiteres Projekt mit einem bereits existierenden Namen
        response = self.client.post('/documents/', {'command': 'projectcreate', 'name': 'user1_project4'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == failure
        self.assertEqual(dictionary['status'], FAILURE)
        # teste ob die richtige Fehlermeldung zurückgegeben wurde
        self.assertEqual(dictionary['response'], ERROR_MESSAGES['PROJECTALREADYEXISTS'].format('user1_project4'))


    # Teste Auflisten aller Projekte:
    # - user1 und user2 besitzen jeweils 2 Projekte, user3 keine
    # - user1 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user2 darf nur seine eigenen Projekte aufgelistet bekommen
    # - user3 bekommt keine Projekte aufgelistet
    def test_listprojects(self):
        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response die beiden erstellten Projekte von user1 richtig aufgelistet werden
        # und keine Projekte von user2 aufgelistet werden
        self.assertEqual(dictionary['response'],
                         [{'id': self._user1_project1.id, 'name': self._user1_project1.name},
                         {'id': self._user1_project2.id, 'name': self._user1_project2.name}])

        # logout von user1
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user2
        self.client.login(username=self._user2.username, password=self._user2._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response die beiden erstellten Projekte von user 2 richtig aufgelistet werden
        # und keine Projekte von user1 aufgelistet werden
        self.assertEqual(dictionary['response'],
                         [{'id': self._user2_project1.id, 'name': self._user2_project1.name},
                         {'id': self._user2_project2.id, 'name': self._user2_project2.name}])

        # logout von user2
        self.client.logout()

        # --------------------------------------------------------------------------------------------------------------
        # login von user3
        self.client.login(username=self._user3.username, password=self._user3._unhashedpw)

        # rufe die URL mit den entsprechenden Parametern zum Auflisten aller Projekte eines Benutzers auf
        response = self.client.post('/documents/', {'command': 'listprojects'})

        # dekodiere den JSON response als dictionary
        dictionary = jsonDecoder(response.content)

        # überprüfe die Antwort des Servers
        # teste, ob status == success
        self.assertEqual(dictionary['status'], SUCCESS)

        # teste, ob in response ein leeres Array übergeben wurde, da user3 keine Projekte besitzt
        self.assertEqual(dictionary['response'], [])

    def test_listfiles(self):
        pass


    def test_downloadfile(self):

        user1_dir = os.path.join(FILEDATA_URL, str(self._user1.id))
        user1_project1_dir = os.path.join(user1_dir, str(self._user1_project1.id))
        if not os.path.isdir(user1_project1_dir):
            os.makedirs(user1_project1_dir)


        rootfolder = self._user1_project1.rootFolder

        folder1 = Folder(name='folder1', parent=rootfolder, root=rootfolder)
        folder1.save()

        folder2 = Folder(name='folder2', parent=rootfolder, root=rootfolder)
        folder2.save()

        folder3 = Folder(name='folder3', parent=rootfolder, root=rootfolder)
        folder3.save()

        subfolder1 = Folder(name='subfolder1', parent=folder3, root=rootfolder)
        subfolder1.save()

        user1_tex1 = TexFile(name='main.tex', folder=subfolder1, source_code='test tex file\n')
        user1_tex1.save()

        user1_bin1 = File(name='test.bin', folder=rootfolder)
        user1_bin1.save()
        file = os.path.join(user1_project1_dir, str(user1_bin1.id))
        user1_binary1_file = open(file, 'w')
        user1_binary1_file.write('test binary file\n')
        user1_binary1_file.close()


        #response = self.client.post('/documents/', {'command': 'downloadfile', 'id': user1_bin1.id})

        response = self.client.post('/documents/', {'command': 'downloadfile', 'id': user1_tex1.id})

        print('response:')
        print(response['Content-Type'])
        print(response['Content-Length'])
        print(response['Content-Disposition'])

        #response = self.client.post('/documents/', {'command': 'listfiles', 'id': rootfolder.id})

        #self.assertEqual(file, smart_str(response.content))

    def test_projectRm(self):
        pass

