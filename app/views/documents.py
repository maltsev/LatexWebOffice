""" 

* Purpose : Dokument- und Projektverwaltung

* Creation Date : 19-11-2014

* Last Modified : Do 20 Nov 2014 14:38:06 CET

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
from app.models.file.document import Document
from app.common.util import jsonDecoder, jsonResponse, jsonErrorResponse, projectToJson
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
        c = available_commands[request.POST['command']]
        # Parameter dieses Befehls
        paras = c['parameters']

        # durchlaufe alle Parameter des Befehls
        for para in paras:
            # wenn der Parameter nicht gefunden wurde, gib Fehlermeldung zurück
            if not request.POST[str(para)]:
                return jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para), request.POST)
            # sonst füge den Parameter zu der Argumentliste hinzu
            else:
                args.append(request.POST[para])

        # versuche den übergebenen Befehl auszuführen
        try:
            return c['command'](request, user, *args)
        # wenn der Schlüssel nicht gefunden wurde
        # gib Fehlermeldung zurück
        except KeyError:
            return jsonErrorResponse(ERROR_MESSAGES['COMMANDNOTFOUND'], request.POST)


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
            texfile = Document.objects.create(name='main.tex', author=user, folder=newproject, source_code='')
            texfile.save()
        except:
            return jsonErrorResponse(ERROR_MESSAGES['EMPTYTEXNOTCREATED'], request)

    return jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)


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
# benötigt: id:rootdirid, name:directoryname
# liefert: HTTP Response (Json)
def createDir(request, user, rootdirid, directoryname):
    pass


# benennt den Ordner mit der angegebenen ID um
# benötigt: id:folderid, name:newdirectoryname
# liefert: HTTP Response (Json)
def renameDir(request, user, folderid, newdirectoryname):
    pass


# löscht den Ordner mit der angegebenen ID
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def rmDir(request, user, folderid):
    pass

# benötigt: id:fileid
# liefert: HTTP Response (Json) --> fileid, filename, folderid, foldername
def fileInfo(request, user, fileid):
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