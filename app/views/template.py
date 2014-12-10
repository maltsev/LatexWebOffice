"""

* Purpose : Verwaltung von Folder Models

* Creation Date : 19-11-2014

* Last Modified : Mi 10 Dez 2014 11:17:56 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 2

* Backlog entry :  DO14

"""
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.common import util
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from django.conf import settings
from django.db import transaction
import mimetypes
import os
import io

# liefert HTTP Response (Json)
# Beispiel response: {}
def template2Project(request, user, vorlageid, projektname):

    #TODO Überprüfe, ob Vorlage existiert und der User darauf Rechte hat

    pass

# liefert: HTTP Response (Json)
# Beispiel response: {type: 'folder', name: 'folder1', id=1, content: {type :


def listFiles(request, user, folderid):
    # Überprüfe ob der user auf den Ordner zugreifen darf und dieser auch
    # existiert
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        folderid, user, request)
    if not rights:
        return failurereturn

    # hole das Ordner Objekt
    current_folderobj = Folder.objects.get(id=folderid)

    # erstelle die Ordner- und Dateistruktur als JSON
    folderandfiles_structure = util.getFolderAndFileStructureAsDict(
        current_folderobj)

    return util.jsonResponse(folderandfiles_structure, True, request)
