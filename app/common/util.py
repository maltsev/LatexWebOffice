# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 23-11-2014

* Last Modified : Mi 03 Dez 2014 14:14:31 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : -

* Backlog entry : -

"""

from django.http import HttpResponse
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE, INVALIDCHARS, ALLOWEDMIMETYPES
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.binaryfile import BinaryFile
from app.models.file.plaintextfile import PlainTextFile
import json, zipfile, os, shutil, tempfile
import mimetypes


# dekodiert ein JSON
def jsonDecoder(responseContent):
    return json.loads(str(responseContent, encoding='utf-8'))


# liefert ein HTTP Response (Json)
def jsonResponse(response, status, request):
    statusstr = FAILURE
    if (status):
        statusstr = SUCCESS

    to_json = {
        'status': statusstr,
        'request': request.POST,
        'response': response
    }

    return HttpResponse(json.dumps(to_json), content_type="application/json")


# liefert jsonResponse Fehlermeldung
def jsonErrorResponse(errormsg, request):
    return jsonResponse(errormsg, False, request)


# liefert die ID und den Namen eines Projektes als dictionary
def projectToJson(project):
    return dict(id=project.id, name=project.name)


# Hilfsmethode um zu überprüfen, ob einer User die Rechte hat einen Ordner zu bearbeiten und ob dieser Ordner existiert
# benötigt: folderid, user, httprequest
def checkIfDirExistsAndUserHasRights(folderid, user, request):
    if not Folder.objects.filter(id=folderid).exists():
        return False, jsonErrorResponse(ERROR_MESSAGES['DIRECTORYNOTEXIST'], request)
    elif not Folder.objects.get(id=folderid).getProject().author == user:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    else:
        return True, None


# Hilfsmethode um zu überprüfen, ob einer User die Rechte hat eine Datei zu bearbeiten und ob diese Datei existiert
# benötigt: fileid, user, httprequest
def checkIfFileExistsAndUserHasRights(fileid, user, request):
    if not File.objects.filter(id=fileid).exists():
        return False, jsonErrorResponse(ERROR_MESSAGES['FILENOTEXIST'], request)
    elif not File.objects.get(id=fileid).folder.getRoot().getProject().author == user:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    else:
        return True, None


# Hilfsmethode um zu überprüfen, ob einer User die Rechte hat ein Projekt zu bearbeiten und ob dieses Projekt existiert
# benötigt: projectid, user, httprequest
def checkIfProjectExistsAndUserHasRights(projectid, user, request):
    if not Project.objects.filter(id=projectid).exists():
        return False, jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTEXIST'], request)
    elif not Project.objects.get(id=projectid).author == user:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    else:
        return True, None


# Hilfsmethode für Django Unit Tests
# prüft ob ein JSON korrekt zurückgeliefert wurde (vgl. jsonResponse(response, status, request) )
# benötigt: self, response.content, status, response (Antwort des Servers)
def _validateServerJsonResponse(self, responsecontent, status, response):
    # dekodiere den JSON response als dictionary
    dictionary = jsonDecoder(responsecontent)

    # Prüfe ob status, request und response in der Antwort enhalten sind
    self.assertIn('status', dictionary)
    self.assertIn('request', dictionary)
    self.assertIn('response', dictionary)

    # Überprüfe, ob der status korrekt ist
    self.assertEqual(dictionary['status'], status)
    # Überprüfe, ob eine korrekte Antwort geliefert wurde
    self.assertEqual(dictionary['response'], response)


# prüft ob ein 'failure' status als JSON zurückgeliefert wurde
# ruft _validateServerJsonResponse auf mit Status 'failure'
def validateJsonFailureResponse(self, responsecontent, errormsg):
    return _validateServerJsonResponse(self, responsecontent, FAILURE, errormsg)


# prüft ob ein 'success' status als JSON zurückgeliefert wurde
# ruft _validateServerJsonResponse auf mit Status 'sucess'
def validateJsonSuccessResponse(self, responsecontent, response):
    return _validateServerJsonResponse(self, responsecontent, SUCCESS, response)


# prüft ob eine Datei oder ein Ordner bereits mit gleichem Namen existiert
# Groß- und Kleinschreibung wird dabei nicht beachtet
# Beispiel: 'user1_project1' und 'USER1_Project1' werden als identisch betrachtet
# Vorraussetzung beim Aufruf: das Objekt existiert in der Datenbank
def checkIfFileOrFolderIsUnique(newname, modelClass, folder, request):
    if modelClass == File:
        if File.objects.filter(name__iexact=newname.lower, folder=folder).exists():
            return False, jsonErrorResponse(ERROR_MESSAGES['FILENAMEEXISTS'], request)
    else:
        if Folder.objects.filter(name__iexact=newname.lower, parent=folder).exists():
            return False, jsonErrorResponse(ERROR_MESSAGES['FOLDERNAMEEXISTS'], request)
    return True, None


# prüft, ob ein Name ungültige Zeichen enthält
# vgl. INVALIDCHARS in /common/constants.py
def checkObjectForInvalidString(name, request):
    if name.isspace():
        return False, jsonErrorResponse(ERROR_MESSAGES['BLANKNAME'], request)
    if any(invalid in name for invalid in INVALIDCHARS):
        return False, jsonErrorResponse(ERROR_MESSAGES['INVALIDNAME'], request)
    return True, None


def _getFoldersAndFiles(folderobj, data={}, printing=False, ident=''):
    data['name'] = folderobj.name
    fileslist = []
    folderslist = []
    data['files'] = fileslist
    data['folders'] = folderslist
    # Hole Files
    files = File.objects.filter(folder=folderobj)
    for f in files:
        if printing:
            print('    ', f)
            print('     ', f.id)
        fileslist.append({'name': f.name, 'id': f.id})

    # Füge rekursiv die Unterordner hinzu
    folders = Folder.objects.filter(parent=folderobj)

    for folder in folders:
        if printing:
            print(folder)
        folderslist.append(_getFoldersAndFiles(folder, data={}, printing=printing, ident=ident + '    '))

    return data


def getProjectFilesFromProjectObject(projectobj, printing=False):
    rootfolder = projectobj.rootFolder

    return _getFoldersAndFiles(rootfolder, printing=printing)


# liefert die Ordner- und Dateistruktur eines gegebenen Ordner Objektes als JSON
def getFolderAndFileStructureAsDict(folderobj):
    return _getFoldersAndFilesJson(folderobj, data={})


def _getFoldersAndFilesJson(folderobj, data={}):
    data['name'] = folderobj.name
    data['id'] = folderobj.id
    filelist = []
    folderlist = []
    data['files'] = filelist
    data['folders'] = folderlist
    files = File.objects.filter(folder=folderobj)
    for f in files:
        filelist.append({'id': f.id, 'name': f.name})

    folders = Folder.objects.filter(parent=folderobj)

    for f in folders:
        folderlist.append(_getFoldersAndFilesJson(f, data={}))

    return data


# Hilfsmethode um leichter die verschiedenen commands durchzutesten.
def documentPoster(self, command='NoCommand', idpara=None, idpara2=None, content=None, name=None, files=None):
    dictionary = {'command': command}
    if idpara != None:
        dictionary['id'] = idpara
    if idpara2 != None:
        dictionary['folderid'] = idpara2
    if content != None:
        dictionary['content'] = content
    if name != None:
        dictionary['name'] = name
    if files != None:
        pass  # TODO
    return self.client.post('/documents/', dictionary)


# Hilfsmethode für hochgeladene Dateien
def uploadFile(f, folder, request,fromZip=False):
    head, name = os.path.split(f.name)
    mime, encoding = mimetypes.guess_type(name)

    # Überprüfe, ob die einzelnen Dateien einen Namen ohne verbotene Zeichen haben
    illegalstring, failurereturn = checkObjectForInvalidString(name, request)
    if not illegalstring:
        return False, ERROR_MESSAGES['INVALIDNAME']


    # Überprüfe auf doppelte Dateien unter Nichtbeachtung Groß- und Kleinschreibung
    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = checkIfFileOrFolderIsUnique(name, File, folder, request)
    if not unique:
        return False, ERROR_MESSAGES['FILENAMEEXISTS']


    # Überprüfe auf verbotene Dateiendungen
    if mime in ALLOWEDMIMETYPES['binary']:
        if not fromZip:
            binfile = BinaryFile.objects.createFromRequestFile(name=name, requestFile=f, folder=folder)
        else:
            binfile=BinaryFile.objects.createFromFile(name=name,filepath=f.name,folder=folder)
        return True, {'name': binfile.name, 'id': binfile.id}
    elif mime in ALLOWEDMIMETYPES['text']:
        if mime==mimetypes.types_map['.tex']:
            try:
                texfile=TexFile(name=name,source_code=f.read().decode('utf-8'),folder=folder)
                # Überprüfe, ob Datenbank Datei speichern kann TODO
                texfile.save()
                return True,{'name':texfile.name,'id':texfile.id}
            except:
                return jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
        else:
            try:
                plainfile = PlainTextFile.objects.create(name=name, source_code=f.read().decode('utf-8'))
                # Überprüfe, ob Datenbank Datei speichern kann
                return True, {'name': plainfile.name, 'id': plainfile.id}
            except:
                return False,jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:  #Unerlaubtes Mimetype
        return False, ERROR_MESSAGES['ILLEGALFILETYPE']


# Erstellt eine zip Datei des übergebenen Ordners inklusive aller Unterordner und zugehöriger Dateien
# folderpath ist der Pfad zum Ordner, aus dem die .zip Datei erstellt werden soll, Beispiel: /home/user/test
# zip_file_path ist der Pfad zur .zip Datei, Beispiel: /home/user/test.zip
def createZipFromFolder(folderpath, zip_file_path):
    relroot = os.path.abspath(folderpath)
    with zipfile.ZipFile(zip_file_path, "w") as zip:
        for root, dirs, files in os.walk(folderpath):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)


# entpackt alle Dateien und Ordner der zip Datei zip_file_path in den Ordner folderpath
def extractZipToFolder(folderpath, zip_file_path):
    zip_file = zipfile.ZipFile(zip_file_path, 'r')
    zip_file.extractall(folderpath)
    zip_file.close()


# liefert die Dateigröße eines file objects in Bytes
# funktioniert auch für StringIO
def getFileSize(pyfile):
    old_file_position = pyfile.tell()
    pyfile.seek(0, os.SEEK_END)
    size = pyfile.tell()
    pyfile.seek(old_file_position, os.SEEK_SET)
    return size


# gibt den Ordnernamen eines Ordnerpfades zurück
def getFolderName(folderpath):
    path, folder_name = os.path.split(folderpath)
    return folder_name
