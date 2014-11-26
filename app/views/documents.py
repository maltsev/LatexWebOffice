""" 

* Purpose : Dokument- und Projektverwaltung

* Creation Date : 19-11-2014

* Last Modified : Tue 25 Nov 2014 09:59:26 PM CET

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
from core.settings import FILEDATA_URL, TMP_FILEDATA_URL
import mimetypes, os

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
        # try: TODO FIX THIS TRY MESS
        return c['command'](request, user, *args)
        #except:
        #    print('Fehler')
        #    to_json['response']=str(sys.exc_info()[0])


# aktualisiert eine geänderte Datei eines Projektes in der Datenbank
# benötigt: id:fileid, content:filecontenttostring
# liefert: HTTP Response (Json)
def updateFile(request, user, fileid, filecontenttostring):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    fileobj = File.objects.get(id=fileid)

    # finde die Dateiendung heraus
    fileName, fileExtension = os.path.splitext(fileobj.name)

    if not fileExtension == '.tex':
        return jsonErrorResponse(ERROR_MESSAGES['NOTEXFILE'], request)

    tex = TexFile.objects.get(id=fileid)

    tex.source_code = filecontenttostring
    tex.save()

    return jsonResponse({}, True, request)


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
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    fileobj = File.objects.get(id=fileid)

    # finde die Dateiendung heraus
    fileName, fileExtension = os.path.splitext(fileobj.name)

    if not fileExtension == '.tex':
        projectid = fileobj.folder.getProject().id
        filepath = os.path.join(FILEDATA_URL, str(user.id), str(projectid), str(fileobj.id))

        os.remove(filepath)

    fileobj.delete()

    return jsonResponse({}, True, request)


# benennt eine vom Client angegebene Datei um
# benötigt: id:fileid, name:newfilename
# liefert: HTTP Response (Json)
def renameFile(request, user, fileid, newfilename):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    emptystring, failurereturn = checkObjectForEmptyString(newfilename, user, request)
    if not emptystring:
        return failurereturn

    fileobj = File.objects.get(id=fileid)

    fileobj.name = newfilename
    fileobj.save()

    return jsonResponse({}, True, request)


# liefert eine Übersicht der Dateien/Unterordner eines Ordners (bzw. Projektes)
# benötigt: id:folderid
# liefert: HTTP Response (Json)
# Beispiel response: {type: 'folder', name: 'folder1', id=1, content: {type :
def listFiles(request, user, folderid):
    # Check if parentdirid exists
    rights, failurereturn = checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    current_folder = Folder.objects.get(id=folderid)

    folderandfiles_structure = listFiles_Helper(current_folder, data={})

    #print(folderandfiles_structure)

    return jsonResponse(folderandfiles_structure, True, request)


def listFiles_Helper(folderobj, data={}):
    data['name'] = folderobj.name
    data['id'] = folderobj.id
    filelist = []
    folderlist = []
    data['files'] = filelist
    data['folders'] = folderlist
    files = File.objects.filter(folder=folderobj)
    for f in files:
        filelist.append({'file': {'id': f.id, 'name': f.name}})

    folders = Folder.objects.filter(parent=folderobj)

    for f in folders:
        folderlist.append({'folder': listFiles_Helper(f, data={})})

    return data


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
        try:
            rootfolder = Folder(name=projectname)
            rootfolder.save()
        except:
            return jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTCREATED'], request)

        # versuche ein neues Projekt zu erstellen
        try:
            newproject = Project(name=projectname, author=user, rootFolder=rootfolder)
            newproject.save()
        except:
            return jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTCREATED'], request)

        # versuche eine neue leere main.tex Datei in dem Projekt zu erstellen
        try:
            texfile = TexFile.objects.create(name='main.tex', folder=rootfolder, source_code='')
            texfile.save()
        except:
            return jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTCREATED'], request)

    return jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)


# löscht ein vorhandenes Projekt eines Benutzers
# benötigt: id:projectid
# liefert: HTTP Response (Json)
def projectRm(request, user, projectid):
    # überprüfe ob das Projekt existiert und der user die Rechte zum Löschen hat
    rights, failurereturn = checkIfProjectExistsAndUserHasRights(projectid, user, request)
    # sonst gib eine Fehlermeldung zurück
    if not rights:
        return failurereturn

    # zu löschendes Projekt
    projectdel = Project.objects.get(id=projectid)

    # TODO zugehörige Dateien und Ordner löschen
    # shutil.rmtree(projectdel.rootFolder)

    # versuche das Projekt zu löschen
    try:
        projectdel.delete()
        return jsonResponse({}, True, request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# importiert ein Projekt aus einer vom Client übergebenen zip Datei
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def importZip(request, user, folderid):
    pass


# liefert eine Übersicht aller Projekte eines Benutzers
# benötigt: nichts
# liefert: HTTP Response (Json)
# Beispiel response:
def listProjects(request, user):
    availableprojects = Project.objects.filter(author=user)

    if availableprojects is None:
        return jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [projectToJson(project) for project in availableprojects]

    return jsonResponse(json_return, True, request)


# liefert eine vom Client angeforderte Datei als Filestream
# benötigt: id:fileid
# liefert: filestream
def downloadFile(request, user, fileid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # lese das File Objekt aus der Datenbank ein
    userfile = File.objects.get(id=fileid)

    # lese die zugehörige Projekt id ein
    userfile_project_id = userfile.folder.getRoot().getProject().id

    # finde die Dateiendung heraus
    fileName, fileExtension = os.path.splitext(userfile.name)

    # wenn eine .tex Datei angefordert wurde
    if fileExtension == '.tex':
        userfile = TexFile.objects.get(id=fileid)
        # erstelle einen Ordner im temp Verzeichnis, falls nicht bereits vorhanden
        # Form ...latexweboffice/temp/projectid/fileid
        userfile_path = os.path.join(TMP_FILEDATA_URL, str(userfile_project_id))
        if not os.path.isdir(userfile_path):
            os.makedirs(userfile_path)
        # erstelle die tex Datei und lese sie ein
        file_dl = open(os.path.join(userfile_path, str(userfile.id)), 'r+')

        file_dl.write(userfile.source_code)
        response = HttpResponse(file_dl.read())
        file_dl.close()

        userfile_path = os.path.join(userfile_path, str(userfile.id))

    # sonst wurde eine Binärdatei angefordert
    else:
        # Pfad zur Binärdatei
        # Form .../latexweboffice/userid/projectid/fileid
        userfile_path = os.path.join(FILEDATA_URL, str(user.id), str(userfile_project_id), str(userfile.id))

        # lese die Datei ein
        file_dl = open(userfile_path, 'r')
        response = HttpResponse(file_dl.read())
        file_dl.close()

    ctype, encoding = mimetypes.guess_type(userfile.name)

    if ctype is None:
        ctype = 'application/octet-stream'
    response['Content-Type'] = ctype
    response['Content-Length'] = str(os.stat(userfile_path).st_size)
    print(userfile_path)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    filename_header = 'filename=%s' % userfile.name.encode('utf-8')

    response['Content-Disposition'] = 'attachment; ' + filename_header

    return response


# liefert ein vom Client angefordertes Projekt in Form einer zip Datei als Filestream
# benötigt: id:folderid
# liefert: filestream
def exportZip(request, user, folderid):
    pass


# erstellt einen neuen Ordner im angegebenen Verzeichnis
# benötigt: id:parentdirid, name:directoryname
# liefert: HTTP Response (Json)
def createDir(request, user, parentdirid, directoryname):
    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    emptystring, failurereturn = checkObjectForEmptyString(directoryname, user, request)
    if not emptystring:
        return failurereturn


        #Check if parentdirid exists
    rights, failurereturn = checkIfDirExistsAndUserHasRights(parentdirid, user, request)
    if not rights:
        return failurereturn

    parentdir = Folder.objects.get(id=parentdirid)


    #Versuche den Ordner in der Datenbank zu speichern
    try:
        newfolder = Folder(name=directoryname, parent=parentdir, root=parentdir.getRoot())
        newfolder.save()
        return jsonResponse({'id': newfolder.id, 'name': newfolder.name, 'parentfolderid': parentdir.id,
                             'parentfoldername': parentdir.name}, True, request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# benennt den Ordner mit der angegebenen ID um
# benötigt: id:folderid, name:newdirectoryname
# liefert: HTTP Response (Json)
def renameDir(request, user, folderid, newdirectoryname):
    rights, failurereturn = checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    folder = Folder.objects.get(id=folderid)


    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    emptystring, failurereturn = checkObjectForEmptyString(folder.name, user, request)
    if not emptystring:
        return failurereturn

    #Versuche die Änderung in die Datenbank zu übernehmen
    try:
        folder.name = newdirectoryname
        folder.save()
        return jsonResponse({'id': folder.id, 'name': folder.name}, True, request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# löscht den Ordner mit der angegebenen ID
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def rmDir(request, user, folderid):
    rights, failurereturn = checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    folder = Folder.objects.get(id=folderid)
    try:
        folder.delete()
        return jsonResponse({}, True, request)
    except:
        return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# benötigt: id:fileid
# liefert: HTTP Response (Json) --> fileid, filename, folderid, foldername
def fileInfo(request, user, fileid):
    rights, failurereturn = checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    fileobj = File.objects.get(id=fileid)
    folder = Folder.objects.get(id=fileobj.folder.id)

    dictionary = {'fileid': fileobj.id, 'filename': fileobj.name, 'folderid': folder.id, 'foldername': folder.name}

    return jsonResponse(dictionary, True, request)



# Kompiliert eine LaTeX Datei
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def latexCompile(request, user, fileid):
    # - Überprüfe, ob es diese Tex-Datei überhaupt gibt und der User die nötigen Rechte auf die Datei hat

    #Aktualisiere Tex Datei in der Datenbank

    #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen
        #- Überprüfe, ob es diese Tex-Datei überhaupt gibt und der User die nötigen Rechte auf die Datei hat
    rights,failurereturn=checkIfFileExistsAndUserHasRights(fileid,user,request)
    if not rights:
        return failurereturn


    #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen
    texfileobj=TexFile.objects.get(id=fileid)
    projectobj=texfileobj.folder.getProject()

    projectDictionaryFileBytes=getProjectBytesFromProjectObject(projectobj)

    #rueckgabe=Sende Dateien an Ingo's Methode

    #Falls rueckgabe okay -> sende pdf von Ingo an client

    #Sonst Fehlermeldung an Client
    return jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)
