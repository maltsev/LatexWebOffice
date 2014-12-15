"""

* Purpose : Verwaltung von File Models

* Creation Date : 19-11-2014

* Last Modified : Fr 12 Dez 2014 14:36:23 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
import mimetypes
import logging
import json

from django.http import HttpResponse, Http404

from app.models.folder import Folder
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.common import util
from app.common.compile import compile as comp
from app.common.constants import ERROR_MESSAGES


# erstellt eine neue .tex Datei in der Datenbank ohne Textinhalt
# benötigt: id:folderid name:texname
# liefert HTTP Response (Json); response: id=fileid, name=filename
def createTexFile(request, user, folderid, texname):
    # hole das Ordner Objekt
    folderobj = Folder.objects.get(id=folderid)

    # Teste ob eine .tex Datei mit dem selben Namen in diesem Ordner schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(texname, File, folderobj, request)
    if not unique:
        return failurereturn

    # versuche die tex Datei zu erstellen
    try:
        texobj = TexFile.objects.create(name=texname, folder=Folder.objects.get(id=folderid), source_code='')
        return util.jsonResponse({'id': texobj.id, 'name': texobj.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# aktualisiert eine geänderte Datei eines Projektes in der Datenbank (akzeptiert nur PlainTextFiles)
# benötigt: id:fileid, content:filecontenttostring
# liefert: HTTP Response (Json)
def updateFile(request, user, fileid, filecontenttostring):
    # wenn es sich bei der Datei nicht um ein PlainTextFile Model aus der Datenbank handelt
    # kann die Datei nicht bearbeitet werden, d.h. es wurde eine Binaryfile übergeben
    if not PlainTextFile.objects.filter(id=fileid).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['NOPLAINTEXTFILE'], request)

    # lese die PlainTextFile Datei ein
    plaintextobj = PlainTextFile.objects.get(id=fileid)

    # versuche den source code in der Datenbank durch den übergebenen String zu ersetzen
    try:
        plaintextobj.source_code = filecontenttostring
        plaintextobj.save()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# löscht eine vom Client angegebene Datei eines Projektes
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def deleteFile(request, user, fileid):
    # hole das file object
    fileobj = File.objects.get(id=fileid)

    # versuche die Datei zu löschen
    try:
        fileobj.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# benennt eine vom Client angegebene Datei um
# benötigt: id:fileid, name:newfilename
# liefert: HTTP Response (Json)
def renameFile(request, user, fileid, newfilename):
    # hole das file object
    fileobj = File.objects.get(id=fileid)

    # Teste ob eine Datei mit dem selben Namen schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(newfilename, File, fileobj.folder, request)
    if not unique:
        return failurereturn

    # versuche den neuen Dateinamen zu setzen
    try:
        fileobj.name = newfilename
        fileobj.save()
        return util.jsonResponse({'id': fileobj.id, 'name': fileobj.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# verschiebt eine Datei in einen anderen Ordner
# benötigt: id: fileid, folderid: newfolderid
# liefert HTTP Response (Json)
def moveFile(request, user, fileid, newfolderid):
    # hole das folder und file object
    folderobj = Folder.objects.get(id=newfolderid)
    fileobj = File.objects.get(id=fileid)

    # Teste ob eine Datei mit dem selben Namen schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(fileobj.name, File, folderobj, request)
    if not unique:
        return failurereturn

    # versuche den neuen Ordner des fileobj zu setzen
    try:
        fileobj.folder = folderobj
        fileobj.save()
        return util.jsonResponse({'id': fileobj.id,
                                  'name': fileobj.name,
                                  'folderid': fileobj.folder.id,
                                  'foldername': fileobj.folder.name,
                                  'rootid': fileobj.folder.getRoot().id}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# speichert vom Client gesendete Dateien im entsprechenden Projektordner
# bzw. in der Datenbank (.tex)/
# benötigt: id:projectid, folderid:folderid
# liefert: HTTP Response (Json)
def uploadFiles(request, user, folderid):
    # dictionary für die Rückgabe von erfolgreich gespeicherten Dateien bzw. fehlgeschlagenen
    # es wird jeweils der name zurückgegeben (bei Erfolg zusätzlich die fileid, bei Fehlschlag der Grund)
    errors = []
    success = []

    folder = Folder.objects.get(id=folderid)

    # Teste ob auch Dateien gesendet wurden
    if not request.FILES and not request.FILES.getlist('files'):
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTALLPOSTPARAMETERS'], request)

    # Hole dateien aus dem request
    files = request.FILES.getlist('files')

    # Gehe die Dateien einzeln durch, bei Erfolg, setze id und name auf die success Liste
    # Bei Fehler, setzte mit name und Grund auf die errors Liste
    for f in files:
        rsp, response = util.uploadFile(f, folder, request)
        if not rsp:
            errors.append({'name': f.name, 'reason': response})
        else:
            success.append(response)

    return util.jsonResponse({'success': success, 'failure': errors}, True, request)


# liefert eine vom Client angeforderte Datei als Filestream
# benötigt: id:fileid
# liefert: filestream
def downloadFile(request, user, fileid):
    # setze das logging level auf ERROR
    # da sonst Not Found: /document/ in der Console bei den Tests ausgegeben wird
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)

    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request)
    if not rights:
        raise Http404

    # setze das logging level wieder auf den ursprünglichen Wert
    logger.setLevel(previous_level)

    if PlainTextFile.objects.filter(id=fileid).exists():
        # hole das Dateiobjekt
        downloadfileobj = PlainTextFile.objects.get(id=fileid)
        # hole den Inhalt des Dateiobjektes
        downloadfileobj_content = downloadfileobj.getContent()

        # ermittle die Dateigröße
        downloadfileobj_size = util.getFileSize(downloadfileobj_content)

        # setze den Inhalt der Datei in response
        response = HttpResponse(downloadfileobj_content.getvalue())
    else:
        # hole das Dateiobjekt
        downloadfileobj = BinaryFile.objects.get(id=fileid)

        # hole den Inhalt des Dateiobjektes
        downloadfileobj_content = open(downloadfileobj.filepath, 'rb')

        # ermittle die Dateigröße
        downloadfileobj_size = util.getFileSize(downloadfileobj_content)
        # setze den Inhalt der Datei in response
        response = HttpResponse(downloadfileobj_content.read())

    downloadfileobj_content.close()

    # versuche den Mimetype herauszufinden
    ctype, encoding = mimetypes.guess_type(downloadfileobj.name)

    # wenn kein Mimetype erkannt wurde, setze den Standard Typ
    if ctype is None:
        ctype = 'application/octet-stream'
    response['Content-Type'] = ctype
    response['Content-Length'] = downloadfileobj_size
    if encoding is not None:
        response['Content-Encoding'] = encoding

    filename_header = 'filename=%s' % downloadfileobj.name

    response['Content-Disposition'] = 'attachment; ' + filename_header

    return response


# benötigt: id:fileid
# liefert: HTTP Response (Json) --> fileid, filename, folderid, foldername
def fileInfo(request, user, fileid):
    # hole das Datei und Ordner Objekt
    fileobj = File.objects.get(id=fileid)
    folderobj = Folder.objects.get(id=fileobj.folder.id)

    # Sende die id und den Namen der Datei sowie des Ordners als JSON response
    dictionary = {'fileid': fileobj.id,
                  'filename': fileobj.name,
                  'folderid': folderobj.id,
                  'foldername': folderobj.name,
                  'projectid': folderobj.getProject().id,
                  'projectname': folderobj.getProject().name,
                  'createdate': util.datetimeToString(fileobj.createTime),
                  'size': fileobj.size,
                  'mimetype': fileobj.mimeType,
                  'ownerid': folderobj.getProject().author.id,
                  'ownername': folderobj.getProject().author.username}

    return util.jsonResponse(dictionary, True, request)


# Kompiliert eine LaTeX Datei
# benötigt: id:fileid
# liefert: HTTP Response (Json)
def latexCompile(request, user, fileid):
    # rueckgabe=Sende Dateien an Ingo's Methode
    errors, success = comp(fileid)
    if errors:
        return util.jsonErrorResponse(json.dumps(errors), request)
    if success:
        return util.jsonResponse(success, True, request)
    # Sonst Fehlermeldung an Client

    return util.jsonErrorResponse(ERROR_MESSAGES['COMPILATIONERROR'], request)
