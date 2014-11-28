# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 23-11-2014

* Last Modified : Fri 28 Nov 2014 10:34:44 PM CET

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
import json
import mimetypes


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


def checkIfFileExistsAndUserHasRights(fileid, user, request):
    if not File.objects.filter(id=fileid).exists():
        return False, jsonErrorResponse(ERROR_MESSAGES['FILENOTEXIST'], request)
    elif not File.objects.get(id=fileid).folder.getRoot().getProject().author == user:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    else:
        return True, None


def validateJsonFailureResponse(self, responsecontent, errormsg):
    return _validateServerJsonResponse(self, responsecontent, FAILURE, errormsg)


def validateJsonSuccessResponse(self, responsecontent, response):
    return _validateServerJsonResponse(self, responsecontent, SUCCESS, response)


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


# Vorraussetzung: das Objekt existiert in der Datenbank
def checkIfFileOrFolderIsUnique(newname, modelClass, folder, request):
    if modelClass == File:
        if File.objects.filter(name__iexact=newname.lower, folder=folder).exists():
            return False, jsonErrorResponse(ERROR_MESSAGES['FILENAMEEXISTS'], request)
    else:
        if Folder.objects.filter(name__iexact=newname.lower, parent=folder).exists():
            return False, jsonErrorResponse(ERROR_MESSAGES['FOLDERNAMEEXISTS'], request)
    return True, None


def checkIfProjectExistsAndUserHasRights(projectid, user, request):
    if not Project.objects.filter(id=projectid).exists():
        return False, jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTEXIST'], request)
    elif not Project.objects.get(id=projectid).author == user:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    else:
        return True, None


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
    # Hole TexFiles
    texfiles = TexFile.objects.filter(folder=folderobj)
    for f in texfiles:
        if printing:
            print('    ', f)
            print('     ', f.source_code)
        fileslist.append({'name': f.name, 'bytes': str.encode(f.source_code)})

    # Hole Binary files
    # TODO

    #Füge rekursiv die Unterordner hinzu
    folders = Folder.objects.filter(parent=folderobj)

    for folder in folders:
        if printing:
            print(folder)
        folderslist.append(_getFoldersAndFiles(folder, data={}, printing=printing, ident=ident + '    '))

    return data


def getProjectBytesFromProjectObject(projectobj):
    rootfolder = projectobj.rootFolder

    return _getFoldersAndFiles(rootfolder, printing=False)


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


def getFolderAndFileStructureAsDict(folderobj):
    return _getFoldersAndFilesJson(folderobj, data={})


# Helper Methode um leichter die verschiedenen commands durchzutesten.
def documentPoster(self, command='NoCommand', idpara=None, idpara2=None, content=None, name=None, files=None):
    dictionary = {'command': command}
    if idpara!=None:
        dictionary['id'] = idpara
    if idpara2!=None:
        dictionary['folderid'] = idpara2
    if content!=None:
        dictionary['content'] = content
    if name!=None:
        dictionary['name'] = name
    if files!=None:
        pass  # TODO
    return self.client.post('/documents/', dictionary)

def uploadFiles(files,folder,request):
    errors=[]
    success=[]

    for f in files:
        mime,encoding=mimetypes.guess_type(f.name)
        
        # Überprüfe, ob die einzelnen Dateien einen Namen ohne verbotene Zeichen haben
        illegalstring, failurereturn = checkObjectForInvalidString(f.name, request)
        if not illegalstring:
            return failurereturn


        #Überprüfe auf doppelte Dateien unter Nichtbeachtung Groß- und Kleinschreibung
        # Teste ob Ordnername in diesem Verzeichnis bereits existiert
        unique, failurereturn = checkIfFileOrFolderIsUnique(f.name, File, folder , request)
        if not unique:
            return failurereturn


        # Überprüfe auf verbotene Dateiendungen
        if mime in ALLOWEDMIMETYPES['binary']:
            pass #TODO waiting for binaryfile constructor
        elif mime in ALLOWEDMIMETYPES['text']:
            if mime=='text/x-tex':
                texfile=TexFile(name=f.name,source_code=f.read().decode('utf-8'),folder=folder)
                # Überprüfe, ob Datenbank Datei speichern kann TODO
                texfile.save()
                success.append({'name':texfile.name,'id':texfile.id})
            else:
                plainfile=PlainTextFile(name=f.name,source_code=f.read().decode('utf-8'))
                # Überprüfe, ob Datenbank Datei speichern kann TODO
                plainfile.save()
                success.append({'name':plainfile.name,'id':plainfile.id})
        else: #Unerlaubtes Mimetype
            errors.append({'name':f.name,'reason':ERROR_MESSAGES['ILLEGALFILETYPE']})
    return jsonResponse({'success':success,'failure':errors},True,request)
