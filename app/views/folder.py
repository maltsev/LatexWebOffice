""" 

* Purpose : Verwaltung von Folder Models

* Creation Date : 19-11-2014

* Last Modified : Sat 29 Nov 2014 12:28:42 AM CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

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


# erstellt einen neuen Ordner im angegebenen Verzeichnis
# benötigt: id:parentdirid, name:directoryname
# liefert: HTTP Response (Json)
def createDir(request, user, parentdirid, directoryname):
    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind
    # nicht erlaubt)
    emptystring, failurereturn = util.checkObjectForInvalidString(
        directoryname,  request)
    if not emptystring:
        return failurereturn

    # Teste ob der übergeordnete Ordner existiert
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        parentdirid, user, request)
    if not rights:
        return failurereturn

    parentdir = Folder.objects.get(id=parentdirid)

    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(
        directoryname, Folder, parentdir, request)
    if not unique:
        return failurereturn

    # Versuche den Ordner in der Datenbank zu speichern
    try:
        newfolder = Folder(
            name=directoryname, parent=parentdir, root=parentdir.getRoot())
        newfolder.save()
        return util.jsonResponse({'id': newfolder.id, 'name': newfolder.name, 'parentfolderid': parentdir.id,
                                  'parentfoldername': parentdir.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# löscht den Ordner mit der angegebenen ID
# benötigt: id:folderid
# liefert: HTTP Response (Json)
def rmDir(request, user, folderid):
    # Teste
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        folderid, user, request)
    if not rights:
        return failurereturn

    folder = Folder.objects.get(id=folderid)

    # Rootfolder dürfen nicht gelöscht werden
    if folder == folder.getRoot():
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)

    try:
        folder.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# benennt den Ordner mit der angegebenen ID um
# benötigt: id:folderid, name:newdirectoryname
# liefert: HTTP Response (Json)
def renameDir(request, user, folderid, newdirectoryname):
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        folderid, user, request)
    if not rights:
        return failurereturn

    folder = Folder.objects.get(id=folderid)

    # Teste, ob der Ordnername keine leeres Wort ist (Nur Leerzeichen sind
    # nicht erlaubt)
    emptystring, failurereturn = util.checkObjectForInvalidString(
        newdirectoryname, request)
    if not emptystring:
        return failurereturn

    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(
        newdirectoryname, Folder, folder.parent, request)
    if not unique:
        return failurereturn

    # Versuche die Änderung in die Datenbank zu übernehmen
    try:
        folder.name = newdirectoryname
        folder.save()
        return util.jsonResponse({'id': folder.id, 'name': folder.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# verschiebt den Ordner mit der angegebenen id in den neuen Ordner mit der newfolderid
# benötigt: id: folderid, folderid: newfolderid
# liefert HTTP Response (Json)
def moveDir(request, user, folderid, newfolderid):
    # Überprüfe ob der zu verschiebende Ordner existiert, und der Benutzer die
    # entsprechenden Rechte besitzt
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        folderid, user, request)
    if not rights:
        return failurereturn

    # Überprüfe ob Ziel Ordner existiert, und der Benutzer die entsprechenden
    # Rechte besitzt
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        newfolderid, user, request)
    if not rights:
        return failurereturn

    folderobj = Folder.objects.get(id=folderid)
    newparentfolderobj = Folder.objects.get(id=newfolderid)

    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(
        folderobj.name, Folder, newparentfolderobj, request)
    if not unique:
        return failurereturn

    # Versuche die Änderung in die Datenbank zu übernehmen
    try:
        # setze den newfolder als neues übergeordnetes Verzeichnis
        folderobj.parent = newparentfolderobj
        # Dessen root Verzeichnis wird auch das Rootverzeichnis vom folderobj
        folderobj.root = newparentfolderobj.getRoot()
        folderobj.save()
        return util.jsonResponse({'id': folderobj.id, 'name': folderobj.name,
                                  'parentid': folderobj.parent.id, 'rootid': folderobj.root.id}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['UNKOWNERROR'], request)


# liefert eine Übersicht der Dateien/Unterordner eines Ordners (bzw. Projektes)
# benötigt: id:folderid
# liefert: HTTP Response (Json)
# Beispiel response: {type: 'folder', name: 'folder1', id=1, content: {type :
def listFiles(request, user, folderid):
    # Überprüfe ob der user auf den Ordner zugreifen darf und dieser auch
    # existiert
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        folderid, user, request)
    if not rights:
        return failurereturn

    current_folder = Folder.objects.get(id=folderid)

    folderandfiles_structure = util.getFolderAndFileStructureAsDict(
        current_folder)

    return util.jsonResponse(folderandfiles_structure, True, request)
