# -*- coding: utf-8 -*-
"""

* Purpose : Verwaltung von File Models

* Creation Date : 19-11-2014

* Last Modified : Mo 23 Feb 2015 17:35:02 CET

* Author :  christian

* Coauthors : mattis, ingo

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
import simplejson as json
import mimetypes
import os
import logging

from datetime import datetime

from django.http import HttpResponse, Http404
from django.views.static import serve

from app.models.folder import Folder
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.models.file.pdf import PDF
from app.common import util
from app.common.compile import latexcompile
from app.common.constants import ERROR_MESSAGES


def createTexFile(request, user, folderid, texname):
    """Erstellt eine neue .tex Datei in der Datenbank ohne Textinhalt.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des Ordners, in welchen die Datei erstellt werden soll
    :param texname: Name der .tex Datei
    :return: HttpResponse (JSON)
    """

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


def updateFile(request, user, fileid, filecontenttostring):
    """Aktualisiert eine geänderte Datei eines Projektes in der Datenbank (akzeptiert nur PlainTextFiles).

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei, welche geändert werden soll
    :param filecontenttostring:  neuer Dateiinhalt als String
    :return: HttpResponse (JSON)
    """

    # lese die PlainTextFile Datei ein
    plaintextobj = PlainTextFile.objects.get(id=fileid)

    isallowedit = not plaintextobj.isLocked() or plaintextobj.lockedBy() == user

    # wenn die Datei vom aktuellen Benutzer nicht bearbeitet werden darf (gesperrt bzw. nicht selber gesperrt)
    if not isallowedit:
        # speichere den Inhalt als neue Datei mit dem aktuellen Datum als Suffix
        newplaintextobj_name = plaintextobj.name + '_' + user.username + '_' \
                               + util.datetimeToString(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        if not PlainTextFile.objects.filter(name=newplaintextobj_name, folder=plaintextobj.folder).exists():

            newplaintextobj = TexFile.objects.create(name=newplaintextobj_name, folder=plaintextobj.folder,
                                                     source_code=filecontenttostring)
            lasteditor = ""
            if plaintextobj.lasteditor:
                plaintextobj.lasteditor.username

            return util.jsonResponse({'id': newplaintextobj.id, 'name': newplaintextobj.name,
                                      'lasteditor': lasteditor},
                                     True, request)
        return util.jsonErrorResponse(ERROR_MESSAGES['FILELOCKED'])

    # sonst sperre die Datei
    plaintextobj.lock(user)

    # versuche den source code in der Datenbank durch den übergebenen String zu ersetzen
    try:
        plaintextobj.source_code = filecontenttostring
        plaintextobj.lasteditor = user
        plaintextobj.save()
        return util.jsonResponse({'id': plaintextobj.id, 'name': plaintextobj.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def deleteFile(request, user, fileid):
    """Löscht eine vom Client angegebene Datei eines Projektes.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei welche gelöscht werden soll
    :return: HttpResponse (JSON)
    """

    # hole das file object
    fileobj = File.objects.get(id=fileid)

    # versuche die Datei zu löschen
    try:
        fileobj.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def renameFile(request, user, fileid, newfilename):
    """Benennt eine vom Client angegebene Datei um.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei welche umbenannt werden soll
    :param newfilename: neuer Dateiname
    :return: HttpResponse (JSON)
    """

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


def moveFile(request, user, fileid, newfolderid):
    """Verschiebt eine Datei in einen anderen Ordner.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei welche verschoben werden soll
    :param newfolderid: Id des Ordners, in welchen die Datei verschoben werden soll
    :return: HttpResponse (JSON)
    """

    # hole das folder und file object
    folderobj = Folder.objects.get(id=newfolderid)
    fileobj = File.objects.get(id=fileid)

    # Teste ob eine Datei mit dem selben Namen schon existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(fileobj.name, File, folderobj, request)
    # Man darf eine Datei in dieselbes Verzeichnis verschieben (dann passiert einfach nichts)
    if not unique and folderobj != fileobj.folder:
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


def uploadFiles(request, user, folderid):
    """Speichert vom Client gesendete Dateien im entsprechenden Projektordner.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des Ordners, in welchen die hochgeladenen Dateien gespeichert werden sollen.
    :return: HttpResponse (JSON)
    """

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


def downloadFile(request, user, fileid):
    """Liefert eine vom Client angeforderte Datei als Filestream.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei welcher heruntergeladen werden soll
    :return: filestream (404 im Fehlerfall)
    """
    # setze das logging level auf ERROR
    # da sonst Not Found: /document/ in der Console bei den Tests ausgegeben wird
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)

    # überprüfe ob der user auf die Datei zugreifen darf und diese auch existiert
    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(fileid, user, request, ['owner', 'collaborator'])
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
        downloadfileobj_content = downloadfileobj.getContent()

        # ermittle die Dateigröße
        downloadfileobj_size = util.getFileSize(downloadfileobj_content)
        # setze den Inhalt der Datei in response
        response = HttpResponse(downloadfileobj_content.read())

    downloadfileobj_content.close()

    # versuche die Kodierung herauszufinden
    _, encoding = mimetypes.guess_type(downloadfileobj.name)

    response['Content-Type'] = downloadfileobj.mimeType
    response['Content-Length'] = len(response.content)
    if encoding is not None:
        response['Content-Encoding'] = encoding

    filename_header = 'filename=%s' % ('\"' + downloadfileobj.name + '\"')

    response['Content-Disposition'] = 'attachment; ' + filename_header

    return response


def getText(request, user, fileid):
    """Liefert eine vom Client angeforderte Text Datei als JSON.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Text Datei welcher heruntergeladen werden soll
    :return: HttpResponse (JSON)
    """

    # hole das tex Datei Objekt
    plaintextobj = PlainTextFile.objects.get(id=fileid)

    isallowedit = not plaintextobj.isLocked() or plaintextobj.lockedBy() == user

    if isallowedit:
        plaintextobj.lock(user)

    lasteditor = ""
    if plaintextobj.lasteditor:
        lasteditor = plaintextobj.lasteditor.username

    dictionary = {
        'fileid': plaintextobj.id,
        'filename': plaintextobj.name,
        'rootid': plaintextobj.folder.getRoot().id,
        'content': plaintextobj.source_code,
        'lastmodifiedtime': util.datetimeToString(plaintextobj.lastModifiedTime),
        'isallowedit': isallowedit,
        'lasteditor': lasteditor
    }

    return util.jsonResponse(dictionary, True, request)

def fileInfo(request, user, fileid):
    """Liefert Informationen zur angeforderten Datei.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei, von der die Informationen angefordert werden
    :return: HttpResponse (JSON)
    """

    # hole das Datei und Ordner Objekt
    fileobj = File.objects.get(id=fileid)
    folderobj = Folder.objects.get(id=fileobj.folder.id)
    # ermittelt das Projekt der Datei
    projectobj = folderobj.getProject()

    # Sende die Datei-Informationen als JSON response

    isallowedit = not fileobj.isLocked() or fileobj.lockedBy() == user

    lasteditor = ""
    if fileobj.lasteditor:
        lasteditor = fileobj.lasteditor.username

    # Sende die id und den Namen der Datei sowie des Ordners als JSON response
    dictionary = {'fileid': fileobj.id,
                  'filename': fileobj.name,
                  'folderid': folderobj.id,
                  'foldername': folderobj.name,
                  'projectid': projectobj.id,
                  'projectname': projectobj.name,
                  'createtime': util.datetimeToString(fileobj.createTime),
                  'lastmodifiedtime': util.datetimeToString(fileobj.lastModifiedTime),
                  'size': fileobj.size,
                  'isallowedit': isallowedit,
                  'lasteditor': lasteditor,
                  'mimetype': fileobj.mimeType,
                  'ownerid': projectobj.author.id,
                  'ownername': projectobj.author.username
    }

    return util.jsonResponse(dictionary, True, request)


def latexCompile(request, user, fileid, formatid, forcecompile):
    """Kompiliert eine LaTeX Datei.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der tex Datei welche kompiliert werden soll
    :param formatid 0 - PDF, 1 - HTML
    :return: HttpResponse (JSON)
    """

    errors, success = latexcompile(fileid, formatid=formatid, forcecompile=forcecompile)
    if errors:
        if success:
            ret = success
        else:
            ret = dict()
        ret['error'] = json.dumps(errors)
        return util.jsonErrorResponse(ret, request)
    if success:
        return util.jsonResponse(success, True, request)

    # Sonst Fehlermeldung an Client
    return util.jsonErrorResponse(ERROR_MESSAGES['COMPILATIONERROR'], request)


def getPDF(request, user, pdfid=None, texid=None, default=''):
    """Liefert die URL einer Datei per GET Request.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param pdfid: Id der PDF Datei, welche angefordert wurde
    :param texid: Id der tex Datei von welcher die PDF Datei angefordert wurde
    :return: URL der Datei
    """

    if (pdfid):
        # PDF Objekt
        pdfobj = PDF.objects.get(id=pdfid)

        # Pfad zur PDF Datei
        filepath = pdfobj.getTempPath()

        return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
    elif (texid):
        #Tex Objekt
        texobj = TexFile.objects.get(id=texid)

        # PDF Objekt, welches zur Tex Datei gehört
        pdfobj = PDF.objects.filter(folder=texobj.folder, name=texobj.name[:-3] + 'pdf')

        if pdfobj.exists():
            # Pfad zur PDF Datei
            filepath = pdfobj[0].getTempPath()

            return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
        else:
            return serve(request, os.path.basename(default), os.path.dirname(default))


def getLog(request, user, fileid):
    """Liefert die Log Datei vom Kompilieren einer Tex Datei.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der tex Datei, von welcher die PDF Datei angefordert wurde
    :return: HttpResponse (JSON)
    """

    # hole das tex Objekt
    texobj = TexFile.objects.get(id=fileid)

    logfilename = texobj.name[:-3] + '<log>'

    logobj = PlainTextFile.objects.filter(name=logfilename, folder=texobj.folder)

    if logobj.exists:
        log = logobj[0].source_code
    else:
        log = ERROR_MESSAGES['NOLOGFILE']

    return util.jsonResponse({'log': log}, True, request)


def lockFile(request, user, fileid):
    """Sperrt die Datei.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei welche gesperrt werden soll
    :return: HttpResponse (JSON)
    """

    file = File.objects.get(pk=fileid)
    if file.isLocked() and file.lockedBy() != user:
        return util.jsonErrorResponse(ERROR_MESSAGES['FILELOCKED'], request)

    file.lock(user)
    return util.jsonResponse({}, True, request)


def unlockFile(request, user, fileid):
    """Entsperrt die Datei.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param fileid: Id der Datei welche entsperrt werden soll
    :return: HttpResponse (JSON)
    """

    file = File.objects.get(pk=fileid)
    if file.isLocked() and file.lockedBy() != user:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNLOCKERROR'], request)

    file.unlock()
    return util.jsonResponse({}, True, request)