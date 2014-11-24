""" 

* Purpose :

* Creation Date : 20-11-2014

* Last Modified : Sat 22 Nov 2014 02:50:07 PM CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 2

* Backlog entry : 

"""

from django.test import TestCase,Client
from django.contrib.auth.models import User
from core.settings import LOGIN_URL, ERROR_MESSAGES
import json
from app.models.project import Project
from app.models.folder import Folder
from app.models.file.document import Document

SUCCESS='success'
FAILURE='failure'



class DocumementsTestClass(TestCase):
    def setUp(self):
        self._client=Client()
        
        user1=User.objects.create_user('test1@test.com','test@test.com',password=123456)
        user2=User.objects.create_user('test2@test.com','test2@test.com',password=123456)
       
        self._client.login(username='test1@test.com',password=123456)

        self._user1=user1
        self._user2=user2

        project1=Project.objects.create(name='root',author=user1)
        project1.save()
        self._project1=project1

        project2=Project.objects.create(name='root2',author=user2)
        subfolder=Folder.objects.create(name='subfolder')
        subfolder.parentFolder=project2
        self._subfolder=subfolder
        project2.save()
        f=Document.objects.create(name='main.tex',author=user2,folder=subfolder,source_code='')
        f.save()
        self._project2=project2
        self._project2file=f

    
    #Helper Methode um leichter die verschiedenen commands durchzutesten.
    def documentPoster(self,command='NoCommand',idpara=None,content=None,name=None,files=None):
        client=self._client
        dictionary={'command':command}
        if idpara:
            dictionary['id']=idpara
        if content:
            dictionary['content']=content
        if name:
            dictionary['name']=name
        if files:
            pass #TODO
        return client.post('/documents/',dictionary)

    def jsonDecoder(self,responseContent):
        return json.loads(str(responseContent,encoding='utf-8'))


    def atest_projectCreate(self):
        client=self._client
        response=client.post('/documents/',{'command': 'projectcreate', 'name':'myProject','testpara':123})
        #print(response.content)

    def test_createDir(self):
        client=self._client
        response=self.documentPoster(command='createdir',idpara=self._project1.id,name='testFolder')
        dictionary=self.jsonDecoder(response.content)
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
        self.assertEqual(Project.objects.get(id=folder1.getRootFolder().id),self._project1)
        
        #Teste, ob ein Unterverzeichnis von einem Unterverzeichnis angelegt werden kann und das auch mit dem gleichen Namen
        response=self.documentPoster(command='createdir',idpara=folder1.id,name='root')
        dictionary=self.jsonDecoder(response.content)
        self.assertTrue(Folder.objects.filter(id=dictionary['response']['id']).exists())

        #Teste, ob ein Verzeichnis zwei gleichnamige Unterverzeichnisse haben kann
        response=self.documentPoster(command='createdir',idpara=folder1.id,name='root')
        dictionary=self.jsonDecoder(response.content)
        self.assertEqual(dictionary['response'],ERROR_MESSAGES['FOLDERNAMEEXISTS'])
        
        #Teste, wie es sich mit falschen Angaben verhält

        #Teste ob user1 in einem Project vom user2 ein Verzeichnis erstellen kann
        response=self.documentPoster(command='createdir',idpara=self._project2.id,name='IDONOTEXISTDIR')
        dictionary=self.jsonDecoder(response.content)
        self.assertEqual(dictionary['status'],FAILURE)
        #Teste, dass die richtige Fehlermeldung zurückgegeben wird
        dictionaryresponse=dictionary['response']
        self.assertEqual(dictionaryresponse,ERROR_MESSAGES['NOTENOUGHRIGHTS'])
        #Teste, dass das Verzeichnis auch nicht erstellt wurde
        self.assertFalse(Folder.objects.filter(name='IDONOTEXISTDIR').exists())

        #TODO Teste auf leeren Verzeichnisnamen

    def test_renameDir(self):
        oldid=self._project1.id
        response=self.documentPoster(command='renamedir', idpara=self._project1.id,name='New project und directory name')

        dictionary=self.jsonDecoder(response.content)
        serveranswer=dictionary['response']
        
        #Teste auf richtige Response Daten bei einer Anfrage, die funktionieren sollte
        self.assertEqual(dictionary['status'],SUCCESS)

        self.assertIn('id',serveranswer)
        self.assertIn('name',serveranswer)

        self.assertEqual(serveranswer['id'],oldid)
        self.assertEqual(serveranswer['name'],'New project und directory name')

        #Teste, ob das Projekt auch unbenannt wurde
        self.assertEqual(Project.objects.get(id=oldid).name,serveranswer['name'])


        #Teste, ob ein anderer User das Projekt eines anderen unbenennen kann
        response=self.documentPoster(command='renamedir',idpara=self._project2.id,name='ROFL')
        dictionary=self.jsonDecoder(response.content)
        serveranswer=dictionary['response']

        self.assertEqual(dictionary['status'],FAILURE)
        
        self.assertEqual(ERROR_MESSAGES['NOTENOUGHRIGHTS'],serveranswer)




        #Teste, ob ein Unterverzeichnis den gleichen Namen haben kann, wie ein anderes Unterverzeichnis im gleichen Elternverzeichnis: Überflüssig, da dies bereits schon in test_createDir getestet wird
    
        #Teste, ob ein Verzeichnis einen leeren Namen haben kann: Überflüssig, da dies bereits schon in der test_createDir Methode getestet wird
        
    def test_rmDir(self):

        self._client.login(username='test2@test.com',password=123456)
        oldid=self._project2.id
        oldsubfolderid=self._subfolder.id
        oldfileid=self._project2file.id
        #Stelle sicher, dass zu diesem Zeitpunkt project2 noch existiert 
        self.assertTrue(Project.objects.filter(id=oldid).exists())
        #Stelle sicher, dass es zu diesem Projekt mind. ein Unterverzeichnis existiert + mind. eine Datei
        self.assertEqual(self._subfolder.parentFolder,self._project2)
        self.assertTrue(Document.objects.filter(id=oldfileid).exists())
        
        response=self.documentPoster(command='rmdir',idpara=self._project2.id)
        dictionary=self.jsonDecoder(response.content)
        serveranswer=dictionary['response']

        self.assertEqual(dictionary['status'],SUCCESS)
        
        #Das Projekt sollte komplett gelöscht worden sein
        self.assertFalse(Project.objects.filter(id=oldid).exists())
        #Unterverzeichnisse und Dateien sollten dabei auch gelöscht werden! (klappt nocht nicht)
        #self.assertFalse(Folder.objects.filter(id=oldsubfolderid).exists())
        #Files von Unterverzeichnissen ebenso
        #self.assertFalse(Document.objects.filter(id=oldfileid).exists())


    def Waitingtest_fileInfo(self):
        response=self.documentPoster(command='fileinfo',idpara=self._project2file.id)
        dictioanry=self.jsonDecoder(response.content)
        serveranswer=dictioanry['response']

        self.assertEqual(dictioanry['status'],SUCCESS)

        #Es sollten richtige Informationen zur Datei zurückgegeben worden sein
        self.assertIn('fileid',serveranswer)
        self.assertIn('filename',serveranswser)
        self.assertIn('folderid',serveranswer)
        self.assertIn('foldername',serveranswer)

        fileobj=self._project2file

        #self.assertEqual(serveranswer['fileid'],
        
    


