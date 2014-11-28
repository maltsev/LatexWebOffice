""" 

* Purpose : Verwaltung von Project Models

* Creation Date : 19-11-2014

* Last Modified : Mi 26 Nov 2014 15:33:04 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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
from django.shortcuts import render_to_response
from django.template import RequestContext


# erzeugt ein neues Projekt für den Benutzer mit einer leeren main.tex Datei
# benötigt: name:projectname
# liefert: HTTP Response (Json)
# Beispiel response: {'name': 'user1_project1', 'id': 1}
def projectCreate(request, user, projectname):
    # Teste, ob der Projektname kein leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    # oder ungültige Sonderzeichen enthält
    emptystring, failurereturn = util.checkObjectForInvalidString(projectname, user, request)
    if not emptystring:
        return failurereturn

    # überprüfe ob ein Projekt mit dem Namen projectname bereits für diese Benutzer existiert
    if Project.objects.filter(name=projectname, author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)
    else:
        try:
            with transaction.atomic():
                rootfolder = Folder.objects.create(name=projectname)
                newproject = Project.objects.create(name=projectname, author=user, rootFolder=rootfolder)
                texfile = TexFile.objects.create(name='main.tex', folder=rootfolder, source_code='')
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
    pass


# liefert ein vom Client angefordertes Projekt in Form einer zip Datei als Filestream
# benötigt: id:folderid
# liefert: filestream
def exportZip(request, user, folderid):
    pass


# gibt ein Projekt für einen anderen Benutzer zum Bearbeiten frei
# benötigt: id: projectid, name:inviteusername
# liefert HTTP Response (Json)
def shareProject(request, user, projectid, inviteusername):
    pass