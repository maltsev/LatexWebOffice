""" 

* Purpose : Dokument- und Projektverwaltung

* Creation Date : 19-11-2014

* Last Modified : Mi 26 Nov 2014 13:22:44 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import sys, traceback
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.common import util
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from django.conf import settings
import mimetypes, os, io
from django.db import transaction

# Verteilerfunktion
# liest den vom Client per POST Data übergebenen Befehl ein
# und führt die entsprechende Methode aus
@login_required
@require_http_methods(['POST'])
def execute(request):
    if request.method == 'POST' and 'command' in request.POST:
        # hole den aktuellen Benutzer
        user = request.user


        globalparas={'id':{'name':'id','type':int},'content':{'name':'content','type':str},'folderid':{'name':'folderid','type':int},'name':{'name':'name','type':str}}

        # dictionary mit verfügbaren Befehlen und den entsprechenden Aktionen
        available_commands = {
            'updatefile': {'command': updateFile, 'parameters': (globalparas['id'], globalparas['content'])},
            'uploadfiles': {'command': uploadFiles, 'parameters': (globalparas['id'], globalparas['folderid'])},
            'deletefile': {'command': deleteFile, 'parameters': (globalparas['id'],)},
            'renamefile': {'command': renameFile, 'parameters': (globalparas['id'], globalparas['name'])},
            'movefile': {'command': moveFile, 'parameters': (globalparas['id'], globalparas['folderid'])},
            'listfiles': {'command': listFiles, 'parameters': (globalparas['id'],)},
            'projectcreate': {'command': projectCreate, 'parameters': (globalparas['name'],)},
            'projectrm': {'command': projectRm, 'parameters': (globalparas['id'],)},
            'importzip': {'command': importZip, 'parameters': (globalparas['id'],)},
            'listprojects': {'command': listProjects, 'parameters': ()},
            'downloadfile': {'command': downloadFile, 'parameters': (globalparas['id'],)},
            'exportzip': {'command': exportZip, 'parameters': (globalparas['id'],)},
            'compile': {'command': latexCompile, 'parameters': (globalparas['id'],)},
            'createdir': {'command': createDir, 'parameters': (globalparas['id'], globalparas['name'])},
            'renamedir': {'command': renameDir, 'parameters': (globalparas['id'], globalparas['name'])},
            'rmdir': {'command': rmDir, 'parameters': (globalparas['id'],)},
            'fileinfo': {'command': fileInfo, 'parameters': (globalparas['id'],)},
            'shareproject': {'command': shareProject, 'parameters': (globalparas['id'], globalparas['name'])}
        }

        # wenn der Schlüssel nicht gefunden wurde
        # gib Fehlermeldung zurück
        if request.POST['command'] not in available_commands:
            return util.jsonErrorResponse(ERROR_MESSAGES['COMMANDNOTFOUND'], request)

        args = []

        # aktueller Befehl
        c = available_commands[request.POST['command']]
        # Parameter dieses Befehls
        paras = c['parameters']

        # durchlaufe alle Parameter des Befehls
        for para in paras:
            # wenn der Parameter nicht gefunden wurde oder ein Parameter, welcher eine id angeben sollte Zeichen enthält, die keine Zahlen sind, gib Fehlermeldung zurück
            if not request.POST.get(para['name']) or (para['type']==int and (not request.POST.get(para['name']).isdigit())):
                request.POST['command']
                request.POST.get(para['name'])
                return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para), request)
            
            # sonst füge den Parameter zu der Argumentliste hinzu
            else:
                args.append(request.POST[para['name']])

        # versuche den übergebenen Befehl auszuführen
        # try: TODO FIX THIS TRY MESS
        return c['command'](request, user, *args)
        #except:
        #    print('Fehler')
        #    to_json['response']=str(sys.exc_info()[0])


    return jsonResponse({}, True, request)
# aktualisiert eine geänderte Datei eines Projektes in der Datenbank
# benötigt: id:fileid, content:filecontenttostring
# liefert: HTTP Response (Json)
def updateFile(request, user, fileid, filecontenttostring):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    if not PlainTextFile.objects.filter(id=fileid).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTEXFILE'], request)

    plaintextobj = PlainTextFile.objects.get(id=fileid)

    plaintextobj.source_code = filecontenttostring
    plaintextobj.save()

    return util.jsonResponse({}, True, request)


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
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    fileobj = File.objects.get(id=fileid)

    # finde die Dateiendung heraus
    fileName, fileExtension = os.path.splitext(fileobj.name)

    if not fileExtension == '.tex':
        projectid = fileobj.folder.getProject().id
        filepath = os.path.join(settings.FILEDATA_URL, str(user.id), str(projectid), str(fileobj.id))

        os.remove(filepath)

    fileobj.delete()

    return util.jsonResponse({}, True, request)


# benennt eine vom Client angegebene Datei um
# benötigt: id:fileid, name:newfilename
# liefert: HTTP Response (Json)
def renameFile(request, user, fileid, newfilename):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    emptystring, failurereturn = util.checkObjectForEmptyString(newfilename, user, request)
    if not emptystring:
        return failurereturn

    fileobj = File.objects.get(id=fileid)

    fileobj.name = newfilename
    fileobj.save()

    return util.jsonResponse({}, True, request)


# liefert eine Übersicht der Dateien/Unterordner eines Ordners (bzw. Projektes)
# benötigt: id:folderid
# liefert: HTTP Response (Json)
# Beispiel response: {type: 'folder', name: 'folder1', id=1, content: {type :
def listFiles(request, user, folderid):
    # Check if parentdirid exists
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    current_folder = Folder.objects.get(id=folderid)

    folderandfiles_structure = util.getFolderAndFileStructureAsDict(current_folder)

    return util.jsonResponse(folderandfiles_structure, True, request)


# erzeugt ein neues Projekt für den Benutzer mit einer leeren main.tex Datei
# benötigt: name:projectname
# liefert: HTTP Response (Json)
# Beispiel response: {'name': 'user1_project1', 'id': 1}
def projectCreate(request, user, projectname):
    # überprüfe ob der Projektname nur aus Leerzeichen besteht
    if projectname.isspace():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTNAMEONLYWHITESPACE'], request)

    # überprüfe ob ein Projekt mit dem Namen projectname bereits für diese Benutzer existiert
    elif Project.objects.filter(name=projectname, author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)
    else:
        try:
            with transaction.atomic():
                rootfolder = Folder(name=projectname)
                rootfolder.save()
                newproject = Project(name=projectname, author=user, rootFolder=rootfolder)
                newproject.save()
                texfile = TexFile.objects.create(name='main.tex', folder=rootfolder, source_code='')
                texfile.save()
        except:
            return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTCREATED'], request)

    return util.jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)


# löscht ein vorhandenes Projekt eines Benutzers
# benötigt: id:projectid
# liefert: HTTP Response (Json)
def projectRm(request, user, projectid):
    # überprüfe ob das Projekt existiert und der user die Rechte zum Löschen hat
    rights, failurereturn = util.checkIfProjectExistsAndUserHasRights(projectid, user, request)
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
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


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
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [util.projectToJson(project) for project in availableprojects]

    return util.jsonResponse(json_return, True, request)


# liefert eine vom Client angeforderte Datei als Filestream
# benötigt: id:fileid
# liefert: filestream
def downloadFile(request, user, fileid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # wenn eine PlainText Datei angefordert wurde
    if PlainTextFile.objects.filter(id=fileid).exists():
        downloadfile = PlainTextFile.objects.get(id=fileid)
        # hole den source code der PlainText Datei
        downloadfile_source_code = downloadfile.source_code
        # erstelle die PlainText Datei als in-memory stream und schreibe den source_code rein
        downloadfileIO = io.StringIO()
        downloadfile_size = downloadfileIO.write(downloadfile_source_code)
        response = HttpResponse(downloadfileIO.getvalue())
        downloadfileIO.close()

    # sonst wurde eine Binärdatei angefordert
    else:
        # Pfad zur Binärdatei
        # Form .../latexweboffice/userid/projectid/fileid

        downloadfile = BinaryFile.objects.get(id=fileid)
        downloadfile_projectid = BinaryFile.objects.get(id=fileid).folder.getProject().id
        downloadfile_path = os.path.join(settings.FILEDATA_URL, str(user.id), str(downloadfile_projectid), str(downloadfile.id))
        downloadfile_size = str(os.stat(downloadfile_path).st_size)

        # lese die Datei ein
        file_dl = open(downloadfile_path, 'r')
        response = HttpResponse(file_dl.read())
        file_dl.close()

    ctype, encoding = mimetypes.guess_type(downloadfile.name)

    if ctype is None:
        ctype = 'application/octet-stream'
    response['Content-Type'] = ctype
    response['Content-Length'] = downloadfile_size
    if encoding is not None:
        response['Content-Encoding'] = encoding

    filename_header = 'filename=%s' % downloadfile.name.encode('utf-8')

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
    emptystring, failurereturn = util.checkObjectForEmptyString(directoryname, user, request)
    if not emptystring:
        return failurereturn


        #Check if parentdirid exists
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(parentdirid, user, request)
    if not rights:
        return failurereturn

    parentdir = Folder.objects.get(id=parentdirid)


    #Versuche den Ordner in der Datenbank zu speichern
    try:
        newfolder = Folder(name=directoryname, parent=parentdir, root=parentdir.getRoot())
        newfolder.save()
        return util.jsonResponse({'id': newfolder.id, 'name': newfolder.name, 'parentfolderid': parentdir.id,
                             'parentfoldername': parentdir.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# benennt den Ordner mit der angegebenen ID um
# benötigt: id:folderid, name:newdirectoryname
# liefert: HTTP Response (Json)
def renameDir(request, user, folderid, newdirectoryname):
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    folder = Folder.objects.get(id=folderid)


    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    emptystring, failurereturn = util.checkObjectForEmptyString(folder.name, user, request)
    if not emptystring:
        return failurereturn

    #Versuche die Änderung in die Datenbank zu übernehmen
    try:
        folder.name = newdirectoryname
        folder.save()
        return util.jsonResponse({'id': folder.id, 'name': folder.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# löscht den Ordner mit der angegebenen ID
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def rmDir(request, user, folderid):
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    folder = Folder.objects.get(id=folderid)
    try:
        folder.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# benötigt: id:fileid
# liefert: HTTP Response (Json) --> fileid, filename, folderid, foldername
def fileInfo(request, user, fileid):
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    fileobj = File.objects.get(id=fileid)
    folder = Folder.objects.get(id=fileobj.folder.id)

    dictionary = {'fileid': fileobj.id, 'filename': fileobj.name, 'folderid': folder.id, 'foldername': folder.name}

    return util.jsonResponse(dictionary, True, request)



# Kompiliert eine LaTeX Datei
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def latexCompile(request, user, fileid):
    # - Überprüfe, ob es diese Tex-Datei überhaupt gibt und der User die nötigen Rechte auf die Datei hat

    #Aktualisiere Tex Datei in der Datenbank

    #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen
        #- Überprüfe, ob es diese Tex-Datei überhaupt gibt und der User die nötigen Rechte auf die Datei hat
    rights,failurereturn=util.checkIfFileExistsAndUserHasRights(fileid,user,request)
    if not rights:
        return failurereturn


    #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen
    texfileobj=TexFile.objects.get(id=fileid)
    projectobj=texfileobj.folder.getProject()

    projectDictionaryFileBytes=util.getProjectBytesFromProjectObject(projectobj)

    #rueckgabe=Sende Dateien an Ingo's Methode

    #Falls rueckgabe okay -> sende pdf von Ingo an client

    #Sonst Fehlermeldung an Client
    return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# gibt ein Projekt für einen anderen Benutzer zum Bearbeiten frei
# benötigt: id: projectid, name:inviteusername
# liefert HTTP Response (Json)
def shareProject(request, user, projectid, inviteusername):
    pass


# verschiebt eine Datei in einen anderen Ordner
# benötigt: id: fileid, folderid: newfolderid
# liefert HTTP Response (Json)
def moveFile(request, user, fileid, newfolderid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    #überprüfe, ob der Ordner mit der id newfolderid existiert und newfolderid dem User gehört
    rights, failurereturn=util.checkIfDirExistsAndUserHasRights(newfolderid,user,request)
    fileobj=File.objects.get(id=fileid)
    if not rights:
        return failurereturn
    folderobj=Folder.objects.get(id=newfolderid)


    fileobj.folder=folderobj

    fileobj.save()

    return util.jsonResponse({},True,request)

    


