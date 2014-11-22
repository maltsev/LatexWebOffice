""" 

* Purpose : Dokument- und Projektverwaltung

* Creation Date : 19-11-2014

* Last Modified : Sat 22 Nov 2014 02:49:28 PM CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
# from models.project import Project
import json
import sys, traceback
from app.models.folder  import Folder
from app.models.project import Project
from app.models.file.file import File
from core.settings import ERROR_MESSAGES



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

        args = []

        # aktueller Befehl
        c=available_commands[request.POST['command']]
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
            if not request.POST[str(para)]:
                to_json['response']='Fehlender Parameter {0}'.format(para)
                return HttpResponse(json.dumps(to_json), content_type="application/json")
            # sonst füge den Parameter zu der Argumentliste hinzu
            else:
                args.append(request.POST[para])

        # versuche den übergebenen Befehl auszuführen
        try:

            return c['command'](request, user, *args)
        # wenn der Schlüssel nicht gefunden wurde
        # gib Fehlermeldung zurück
        except KeyError:
            to_json['response']= 'Befehl nicht gefunden'
        #except:
        #    to_json['response']=str(sys.exc_info()[0])
        return HttpResponse(json.dumps(to_json), content_type="application/json")

# liefert ein HTTP Response (Json)
def jsonResponse(dictionary, status, request):
    statusstr = 'failure'

    if(status):
        statusstr = 'success'

    to_json = {
        'status': statusstr,
        'request': request.POST,
        'response': dictionary
    }

    return HttpResponse(json.dumps(to_json), content_type="application/json")

def jsonErrorResponse(errormsg,request):
    return jsonResponse(errormsg,False,request)

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
def projectCreate(request, user, projectname):
    to_json = {
        'status': 'success',
        'command': request.POST['command'],
        'parameters': None,
        'reason': 'Projekt Erstellung erfolgreich'
    }


    return HttpResponse(json.dumps(to_json), content_type="application/json")


# importiert ein Projekt aus einer vom Client übergebenen zip Datei
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def importZip(request, user, folderid):
    pass


# liefert eine Übersicht aller Projekte eines Benutzers
# benötigt: nichts
# liefert: HTTP Response (Json)
def listProjects(request, user):
    pass


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

# Hilfsmethode um zu überprüfen, ob einer User überhaupt die Rechte hat einen Ordner zu bearbeiten und ob dieser Ordner existiert
# benötigt: folderid, user, httprequest
def checkIfDirExistsAndUserHasRights(folderid,user,request):
    if not Folder.objects.filter(id=folderid).exists():
        return False,jsonErrorResponse(ERROR_MESSAGES['DIRECTORYNOTEXIST'],request)
    elif not Project.objects.get(id=Folder.objects.get(id=folderid).getRootFolder().id).author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None

def checkIfFileExistsAndUserHasRights(fileid,user,request):
    if not File.objects.filter(id=fileid).exists():
        return False,jsonErrorResponse(ERROR_MESSAGES['FILENOTEXIST'],request)
    elif not File.objects.get(id=fileid).author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None
    

# erstellt einen neuen Ordner im angegebenen Verzeichnis
# benötigt: id:parentdirid, name:directoryname
# liefert: HTTP Response (Json)
def createDir(request, user, parentdirid, directoryname):
    #Check if parentdirid exists

    rights,failurereturn=checkIfDirExistsAndUserHasRights(parentdirid,user,request)
    if not rights:
        return failurereturn


    parentdir=Folder.objects.get(id=parentdirid) 


    ################################
    
    
    
    #Test for empty strings
    
    
    subfolders=parentdir.folder_set.all()
    for f in subfolders:
        if f.name==directoryname[:255]: #TODO diesen check muss die Datenbank machen!!!
            return jsonErrorResponse(ERROR_MESSAGES['FOLDERNAMEEXISTS'],request)

    ################################
    
    #Versuche den Ordner in der Datenbank zu speichern 
    try:
        newfolder=Folder(name=directoryname,parentFolder=parentdir)
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

    ################################



    #Test for empty strings

    subfolders=folder.folder_set.all()
    if folder.parentFolder:
        subfolders=folder.parentFolder.folder_set.all()
    for f in subfolders:
        if f.name==newdirectoryname[:255]: #TODO diesen check muss die Datenbank machen!!!
            return jsonErrorResponse(ERROR_MESSAGES['FOLDERNAMEEXISTS'],request)

    ################################
    
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
#TODO funktioniert noch nicht
   # rights,failurereturn=checkIfFileExistsAndUserHasRights(fileid,user,request)
   # if not rights:
   #     return failurereturn

   # fileobj=File.objects.get(id=fileid)
   # folder=Folder.objects.get(id=fileobj.folder.id)

    #dictionary={'fileid':fileobj.id,'filename':fileobj.name,'folderid':folder.obj,'foldername':folder.name}

    #return jsonResponse(dictionary,True,request)
    pass

# Kompiliert eine LaTeX Datei
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def latexCompile(request, user, fileid):
    """TODO: Docstring for exportToPdf.

    :request: A (POST) HttpRequest that has the following data: 
    texid: The id of the tex file
    content: The contents of the tex file
    :returns: TODO

    """
    #Get username
    user = request.user
    to_json = {
        'status': 'success',
        'message': 'you failed',
        'content': None
    }

    if ('texid' in request.POST and 'content' in request.POST):
        texid = request.POST['texid']
        content = request.POST['content']


        #- Überprüfe, ob es diese Tex-Datei überhaupt gibt

        #Aktualisiere Tex Datei in der Datenbank

        #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen

        #rueckgabe=Sende Dateien an Ingo's Methode

        #Falls rueckgabe okay -> sende pdf von Ingo an client

        #Sonst Fehlermeldung an Client
        to_json = {
            'status': 'success',
            'message': 'you failed',
            'content': None
        }
    return HttpResponse(json.dumps(to_json), content_type="application/json")
