""" 

* Purpose : Dokument- und Projektverwaltung

* Creation Date : 19-11-2014

* Last Modified : Di 25 Nov 2014 16:33:23 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import json
import sys, traceback
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.common.util import *
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE

# Verteilerfunktion
# liest den vom Client per POST Data übergebenen Befehl ein
# und führt die entsprechende Methode aus
@login_required
def execute(request):
    if request.method == 'POST' and 'command' in request.POST:
        # hole den aktuellen Benutzer
        user = request.user

        # dictionary mit verfügbaren Befehlen und den entsprechenden Aktionen
        available_commands = {
            'updatefile': {'command': updateFile, 'parameters': ('id', 'content')},
            'uploadfiles': {'command': uploadFiles, 'parameters': ('id', 'folderid')},
            'deletefile': {'command': deleteFile, 'parameters': ('id',)},
            'renamefile': {'command': renameFile, 'parameters': ('id', 'name')},
            'listfiles': {'command': listFiles, 'parameters': ('id',)},
            'projectcreate': {'command': projectCreate, 'parameters': ('name',)},
            'projectrm': {'command': projectRm, 'parameters': ('id',)},
            'importzip': {'command': importZip, 'parameters': ('id',)},
            'listprojects': {'command': listProjects, 'parameters': ()},
            'downloadfile': {'command': downloadFile, 'parameters': ('id',)},
            'exportzip': {'command': exportZip, 'parameters': ('id',)},
            'compile': {'command': latexCompile, 'parameters': ('id',)},
            'createdir': {'command': createDir, 'parameters': ('id', 'name')},
            'renamedir': {'command': renameDir, 'parameters': ('id', 'name')},
            'rmdir': {'command': rmDir, 'parameters': ('id',)},
            'fileinfo': {'command': fileInfo, 'parameters': ('id',)}
        }

        # wenn der Schlüssel nicht gefunden wurde
        # gib Fehlermeldung zurück
        if request.POST['command'] not in available_commands:
            return jsonErrorResponse(ERROR_MESSAGES['COMMANDNOTFOUND'], request)

        args = []

        # aktueller Befehl
        c = available_commands[request.POST['command']]
        # Parameter dieses Befehls
        paras = c['parameters']


        to_json = {
            'status': 'failure',
            'request': request.POST,
            'response': ''
            }

        # durchlaufe alle Parameter des Befehls
        for para in paras:
            # wenn der Parameter nicht gefunden wurde, gib Fehlermeldung zurück
            if not request.POST.get(para):
                return jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para), request)
            # sonst füge den Parameter zu der Argumentliste hinzu
            else:
                args.append(request.POST[para])

        # versuche den übergebenen Befehl auszuführen
        #try: TODO FIX THIS TRY MESS
        return c['command'](request, user, *args)
        #except:
        #    print('Fehler')
        #    to_json['response']=str(sys.exc_info()[0])


# aktualisiert eine geänderte Datei eines Projektes in der Datenbank
# benötigt: id:fileid, content:filecontenttostring
# liefert: HTTP Response (Json)
def updateFile(request, user, fileid, filecontenttostring):
    pass


# speichert vom Client gesendete Dateien im entsprechenden Projektordner
# bzw. in der Datenbank (.tex)
# benötigt: id:projectid, folderid:folderid
# liefert: HTTP Response (Json)
def uploadFiles(request, user, projectid, folderid):
    pass


# löscht eine vom Client angegebene Datei eines Projektes
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def deleteFile(request, user, fileid):
    pass


# benennt eine vom Client angegebene Datei um
# benötigt: id:fileid, name:newfilename
# liefert: HTTP Response (Json)
def renameFile(request, user, fileid, newfilename):
    pass


# liefert eine Übersicht der Dateien/Unterordner eines Ordners (bzw. Projektes)
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def listFiles(request, user, folderid):
    pass


# erzeugt ein neues Projekt für den Benutzer mit einer leeren main.tex Datei
# benötigt: name:projectname
# liefert: HTTP Response (Json)
# Beispiel response: {'name': 'user1_project1', 'id': 1}
def projectCreate(request, user, projectname):
    # überprüfe ob der Projektname nur aus Leerzeichen besteht
    if projectname.isspace():
        return jsonErrorResponse(ERROR_MESSAGES['PROJECTNAMEONLYWHITESPACE'], request)

    # überprüfe ob ein Projekt mit dem Namen projectname bereits für diese Benutzer existiert
    elif Project.objects.filter(name=projectname, author=user).exists():
        return jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)
    else:
        # versuche ein neues Projekt zu erstellen
        try:
            newproject = Project(name=projectname, author=user)
            newproject.save()
        except:
            return jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTCREATED'], request)

        # versuche eine neue leere main.tex Datei in dem Projekt zu erstellen
        try:
            texfile = TexFile.objects.create(name='main.tex', author=user, folder=newproject, source_code='')
            texfile.save()
        except:
            return jsonErrorResponse(ERROR_MESSAGES['EMPTYTEXNOTCREATED'], request)

    return jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)


# löscht ein vorhandenes Projekt eines Benutzers
# benötigt: id:projectid
# liefert: HTTP Response (Json)
def projectRm(request, user, projectid):
    pass


# importiert ein Projekt aus einer vom Client übergebenen zip Datei
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def importZip(request, user, folderid):
    pass


# liefert eine Übersicht aller Projekte eines Benutzers
# benötigt: nichts
# liefert: HTTP Response (Json)
# Beispiel response: [{'id': 1, 'name': 'user1_project1'}, {'id': 2, 'name': 'user1_project2'}, ...]
def listProjects(request, user):
    availableprojects = Project.objects.filter(author=user)

    if availableprojects == None:
        json_return = []
    else:
        json_return = [projectToJson(project) for project in availableprojects]

    return jsonResponse(json_return, True, request)



# liefert eine vom Client angeforderte Datei als Filestream
# benötigt: id:fileid
# liefert: filestream
def downloadFile(request, user, fileid):
    pass


# liefert ein vom Client angefordertes Projekt in Form einer zip Datei als Filestream
# benötigt: id:folderid
# liefert: filestream
def exportZip(request, user, folderid):
    pass


# erstellt einen neuen Ordner im angegebenen Verzeichnis
# benötigt: id:parentdirid, name:directoryname
# liefert: HTTP Response (Json)
def createDir(request, user, parentdirid, directoryname):
    
    #Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)  
    emptystring,failurereturn=checkObjectForEmptyString(directoryname,user,request)
    if not emptystring:
        return failurereturn
   
   
   #Check if parentdirid exists
    rights,failurereturn=checkIfDirExistsAndUserHasRights(parentdirid,user,request)
    if not rights:
        return failurereturn


    parentdir=Folder.objects.get(id=parentdirid) 

    
   #Versuche den Ordner in der Datenbank zu speichern 
    try:
        newfolder=Folder(name=directoryname,parent=parentdir,root=parentdir.getRoot())
        newfolder.save()
        return jsonResponse({'id':newfolder.id,'name':newfolder.name,'parentfolderid':parentdir.id,'parentfoldername':parentdir.name},True,request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'],request)



# benennt den Ordner mit der angegebenen ID um
# benötigt: id:folderid, name:newdirectoryname
# liefert: HTTP Response (Json)
def renameDir(request, user, folderid, newdirectoryname):

    rights,failurereturn=checkIfDirExistsAndUserHasRights(folderid,user,request)
    if not rights:
        return failurereturn

    folder=Folder.objects.get(id=folderid) 


    #Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)  
    emptystring,failurereturn=checkObjectForEmptyString(folder.name,user,request)
    if not emptystring:
        return failurereturn
   
    #Versuche die Änderung in die Datenbank zu übernehmen
    try:
        folder.name=newdirectoryname
        folder.save()
        return jsonResponse({'id':folder.id,'name':folder.name},True,request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'],request)



# löscht den Ordner mit der angegebenen ID
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def rmDir(request, user, folderid):

    rights,failurereturn=checkIfDirExistsAndUserHasRights(folderid,user,request)
    if not rights:
        return failurereturn

    folder=Folder.objects.get(id=folderid)
    try:
        folder.delete()
        return jsonResponse({},True,request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'],request)



# benötigt: id:fileid
# liefert: HTTP Response (Json) --> fileid, filename, folderid, foldername
def fileInfo(request, user, fileid):
    rights,failurereturn=checkIfFileExistsAndUserHasRights(fileid,user,request)
    if not rights:
        return failurereturn

    fileobj=File.objects.get(id=fileid)
    folder=Folder.objects.get(id=fileobj.folder.id)

    dictionary={'fileid':fileobj.id,'filename':fileobj.name,'folderid':folder.obj,'foldername':folder.name}

    return jsonResponse(dictionary,True,request)

# Kompiliert eine LaTeX Datei
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def latexCompile(request, user, fileid):
        #- Überprüfe, ob es diese Tex-Datei überhaupt gibt und der User die nötigen Rechte auf die Datei hat
         
        #Aktualisiere Tex Datei in der Datenbank

        #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen

        #rueckgabe=Sende Dateien an Ingo's Methode

        #Falls rueckgabe okay -> sende pdf von Ingo an client

        #Sonst Fehlermeldung an Client
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'],request)
