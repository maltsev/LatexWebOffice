""" 

* Purpose : Verwaltung von Project Models

* Creation Date : 19-11-2014

* Last Modified : Fri 28 Nov 2014 10:32:47 PM CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
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
import mimetypes, os, io, tempfile, zipfile
from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext


# erzeugt ein neues Projekt für den Benutzer mit einer leeren main.tex Datei
# benötigt: name:projectname
# liefert: HTTP Response (Json)
# Beispiel response: {'name': 'user1_project1', 'id': 1}
def projectCreate(request, user, projectname):
    # Teste, ob der Projektname kein leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    # oder ungültige Sonderzeichen enthält
    emptystring, failurereturn = util.checkObjectForInvalidString(projectname, request)
    if not emptystring:
        return failurereturn

    # überprüfe ob ein Projekt mit dem Namen projectname bereits für diese Benutzer existiert
    if Project.objects.filter(name=projectname, author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)
    else:
        try:
            with transaction.atomic():
                newproject = Project.objects.create(name=projectname, author=user)
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

    # hole das zu löschende Projekt
    projectdel = Project.objects.get(id=projectid)

    # versuche das Projekt zu löschen
    try:
        projectdel.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


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


# importiert ein Projekt aus einer vom Client übergebenen zip Datei
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def importZip(request, user, folderid):
    # Teste ob der Ordner existiert und der User rechte auf dem Ordner hat
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        return failurereturn
    folder=Folder.objects.get(id=folderid)

    # Teste ob auch Dateien gesendet wurden
    if not request.FILES and not request.FILES.getlist('files'):
       return util.jsonErrorResponse(ERROR_MESSAGES['NOTALLPOSTPARAMETERS'],request)

    # Hole dateien aus dem request
    files=request.FILES.getlist('files')

    # Erstelle ein temp Verzeichnis, in welches die .zip Datei entpackt werden soll
    _, tmp = tempfile.mkstemp()

    # speichere die .zip Datei im tmp Verzeichnis
    zip_file_path = os.path.join(tmp, files[0].name)
    zip_file = open(zip_file_path, 'rb')
    zip_file.write(files[0].read())
    zip_file.close()

    # überprüfe ob es sich um eine gültige .zip Datei handelt
    if not zipfile.is_zipfile(zip_file_path):
        return util.jsonErrorResponse(ERROR_MESSAGES['ILLEGALFILETYPE'], request)
    # entpacke die .zip Datei in .../tmp/extracted
    extract_path = os.path.join(tmp, 'extracted')
    util.extractZipToFolder(extract_path, zip_file_path)

    # durchlaufe alle Dateien und Ordner in extracted

    # wenn der Ordner oder Dateiname gültig ist

    # speichere die Datei/den Ordner in der Datenbank



    return util.jsonResponse({}, True, request)


# liefert ein vom Client angefordertes Projekt in Form einer zip Datei als Filestream
# benötigt: id:folderid
# liefert: filestream
def exportZip(request, user, folderid):
    # Überprüfe ob der Ordner existiert, und der Benutzer die entsprechenden Rechte besitzt
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(folderid, user, request)
    if not rights:
        raise Http404

    # hole das Ordner Objekt
    folderobj = Folder.objects.get(id=folderid)

    # erstelle ein temp Verzeichnis mit alle Dateien und Unterordnern des gegegeben Ordners
    _, tmp = tempfile.mkstemp()

    # TODO alle Unterordner und Dateien des Ordners in das tmp Verzeichnis kopieren

    # Unterorder im tmp Verzeichnis, das zur zip Datei hinzugefügt werden soll
    tmp_folder = os.path.join(tmp, folderobj.name)

    # erstelle die .zip Datei
    util.createZipFromFolder(tmp_folder, os.path.join(tmp, folderobj.name + '.zip'))

    # lese die erstellte .zip Datei ein
    file_dl_path = os.path.join(tmp_folder, folderobj.name, '.zip')
    file_dl = open(file_dl_path, 'rb')

    response = HttpResponse(file_dl.read())

    file_dl.close()

    file_dl_size = str(os.stat(file_dl_path).st_size)

    ctype, encoding = mimetypes.guess_type(folderobj.name + '.zip')

    if ctype is None:
        ctype = 'application/octet-stream'
    response['Content-Type'] = ctype
    response['Content-Length'] = file_dl_size
    if encoding is not None:
        response['Content-Encoding'] = encoding

    filename_header = 'filename=%s' % (folderobj.name + '.zip').encode('utf-8')

    response['Content-Disposition'] = 'attachment; ' + filename_header

    return response



# gibt ein Projekt für einen anderen Benutzer zum Bearbeiten frei
# benötigt: id: projectid, name:inviteusername
# liefert HTTP Response (Json)
def shareProject(request, user, projectid, inviteusername):
    pass
