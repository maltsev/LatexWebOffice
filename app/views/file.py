"""

* Purpose : Verwaltung von File Models

* Creation Date : 19-11-2014

* Last Modified : Sat 29 Nov 2014 01:49:37 AM CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.http import HttpResponse, Http404
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

# erstellt eine neue .tex Datei in der Datenbank ohne Textinhalt
# benötigt: id:folderid name:filename
# liefert HTTP Response (Json); response: id=fileid, name=filename
def createTexFile(request, user, folderid, texname):
    # Überprüfe ob der Ordner existiert, und der Benutzer die entsprechenden Rechte besitzt
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn

    file_folder = Folder.objects.get(id=folderid)

    # Teste ob eine .tex Datei mit dem selben Namen schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(texname, File, file_folder, request)
    if not unique:
        return failurereturn

    # Teste, ob der Dateiname kein leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    # oder ungültige Sonderzeichen enthält
    emptystring, failurereturn = util.checkObjectForInvalidString(texname, request)
    if not emptystring:
        return failurereturn
    try:
        texobj = TexFile.objects.create(name=texname, folder=Folder.objects.get(id=folderid), source_code='')
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['FILENOTCREATED'], request)

    return util.jsonResponse({'id': texobj.id, 'name': texobj.name}, True, request)


# aktualisiert eine geänderte Datei eines Projektes in der Datenbank
# benötigt: id:fileid, content:filecontenttostring
# liefert: HTTP Response (Json)
def updateFile(request, user, fileid, filecontenttostring):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # wenn es sich bei der Datei nicht um ein PlainTextFile Model aus der Datenbank handelt
    # kann die Datei nicht bearbeitet werden, d.h. es wurde eine Binaryfile übergeben
    if not PlainTextFile.objects.filter(id=fileid).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['NOPLAINTEXTFILE'], request)

    # lese die PlainTextFile Datei ein
    plaintextobj = PlainTextFile.objects.get(id=fileid)

    # ersetze den source code in der Datenbank durch den übergebenen String
    plaintextobj.source_code = filecontenttostring
    plaintextobj.save()

    return util.jsonResponse({}, True, request)


# löscht eine vom Client angegebene Datei eines Projektes
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def deleteFile(request, user, fileid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # hole das file object
    fileobj = File.objects.get(id=fileid)

    # lösche die Datei
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

    # Teste, ob der filename keine leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    emptystring, failurereturn = util.checkObjectForInvalidString(newfilename, request)
    if not emptystring:
        return failurereturn

    # hole das file object
    fileobj = File.objects.get(id=fileid)

    # Teste ob eine Datei mit dem selben Namen schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(newfilename, File, fileobj.folder, request)
    if not unique:
        return failurereturn

    # setze den neuen Dateinamen und speichere das Objekt
    fileobj.name = newfilename
    fileobj.save()

    return util.jsonResponse({}, True, request)


# verschiebt eine Datei in einen anderen Ordner
# benötigt: id: fileid, folderid: newfolderid
# liefert HTTP Response (Json)
def moveFile(request, user, fileid, newfolderid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn

    # überprüfe, ob die Datei mit der id fileid existiert und newfolderid dem User gehört
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(newfolderid, user, request)
    fileobj = File.objects.get(id=fileid)
    if not rights:
        return failurereturn

    # hole das folder und file object
    folderobj = Folder.objects.get(id=newfolderid)
    fileobj = File.objects.get(id=fileid)

    # Teste ob eine Datei mit dem selben Namen schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(fileobj.name, File, folderobj, request)
    if not unique:
        return failurereturn

    # setze den neuen Ordner des folderobj und speichere die Änderung
    fileobj.folder = folderobj
    fileobj.save()

    return util.jsonResponse({}, True, request)


# speichert vom Client gesendete Dateien im entsprechenden Projektordner
# bzw. in der Datenbank (.tex)/
# benötigt: id:projectid, folderid:folderid
# liefert: HTTP Response (Json)
def uploadFiles(request, user, folderid):

    errors=[]
    success=[]
    

    
    # Teste ob der Ordner existiert und der User rechte auf dem Ordner hat
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        print('fuck')
        return failurereturn
    folder=Folder.objects.get(id=folderid)
    
    # Teste ob auch Dateien gesendet wurden
    if not request.FILES and not request.FILES.getlist('files'):
       return util.jsonErrorResponse(ERROR_MESSAGES['NOTALLPOSTPARAMETERS'],request)
    
    # Hole dateien aus dem request
    files=request.FILES.getlist('files')


    # Gehe die Dateien einzeln durch, bei Erfolg, setze id und name auf die success Liste
    # Bei Fehler, setzte mit name und Grund auf die errors Liste
    for f in files:
        rsp,response=util.uploadFile(f,folder,request)
        if not rsp:
            errors.append({'name':f.name,'reason':response})
        else:
            success.append(response)

    

    return util.jsonResponse({'success':success,'failure':errors},True,request)


# liefert eine vom Client angeforderte Datei als Filestream
# benötigt: id:fileid
# liefert: filestream
def downloadFile(request, user, fileid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        raise Http404

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
        downloadfile_path = os.path.join(settings.FILEDATA_URL, str(user.id), str(downloadfile_projectid),
                                         str(downloadfile.id))
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


# benötigt: id:fileid
# liefert: HTTP Response (Json) --> fileid, filename, folderid, foldername
def fileInfo(request, user, fileid):
    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
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

    # Aktualisiere Tex Datei in der Datenbank

    # Zum Projekt der Tex-Datei dazugehörende Dateien abrufen
    # - Überprüfe, ob es diese Tex-Datei überhaupt gibt und der User die nötigen Rechte auf die Datei hat
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        return failurereturn


    # Zum Projekt der Tex-Datei dazugehörende Dateien abrufen
    texfileobj = TexFile.objects.get(id=fileid)
    projectobj = texfileobj.folder.getProject()

    projectDictionaryFileBytes = util.getProjectBytesFromProjectObject(projectobj)

    # rueckgabe=Sende Dateien an Ingo's Methode

    # Falls rueckgabe okay -> sende pdf von Ingo an client

    # Sonst Fehlermeldung an Client
    return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)
