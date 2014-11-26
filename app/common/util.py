# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 23-11-2014

* Last Modified : Mi 26 Nov 2014 16:05:19 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : -

* Backlog entry : -

"""

from django.http import HttpResponse
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE, INVALIDCHARS
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
import json


def jsonDecoder(responseContent):
    return json.loads(str(responseContent, encoding='utf-8'))


# liefert ein HTTP Response (Json)
def jsonResponse(response, status, request):
    statusstr = FAILURE
    if(status):
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


# Hilfsmethode
# liefert die ID und den Namen eines Projektes als dictionary
def projectToJson(project):
    return dict(id=project.id, name=project.name)


# Hilfsmethode um zu überprüfen, ob einer User überhaupt die Rechte hat einen Ordner zu bearbeiten und ob dieser Ordner existiert
# benötigt: folderid, user, httprequest
def checkIfDirExistsAndUserHasRights(folderid,user,request):
    if not Folder.objects.filter(id=folderid).exists():
        return False,jsonErrorResponse(ERROR_MESSAGES['DIRECTORYNOTEXIST'],request)
    elif not Folder.objects.get(id=folderid).getProject().author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None

def checkIfFileExistsAndUserHasRights(fileid,user,request):
    if not File.objects.filter(id=fileid).exists():
        return False,jsonErrorResponse(ERROR_MESSAGES['FILENOTEXIST'],request)
    elif not File.objects.get(id=fileid).folder.getRoot().getProject().author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None

# Vorraussetzung: das Objekt existiert in der Datenbank
def checkIfFileOrFolderAlreadyExists(idpara,newname,modelObj):
    oldobj=modelObj.objects.get(id=idpara)

    if type(modelObj)==File:
        folder=oldobj.folder
        for dirfile in modelObj.objects.filter(folder=folder):
            if dirfile.name.lower()==newname.lower():
                return False,jsonErrorResponse(ERROR_MESSAGES['FILENAMEEXISTS'])

    else:
        folder=oldobj.parent
        for dirobj in modelObj.objects.filter(parent=folder):
            if dirobj.name.lower()==newname.lower():
                return False,jsonErrorResponse(ERROR_MESSAGES['FOLDERNAMEEXISTS'])
    return True,None


def checkIfProjectExistsAndUserHasRights(projectid,user,request):
    if not Project.objects.filter(id=projectid).exists():
        return False,jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTEXIST'],request)
    elif not Project.objects.get(id=projectid).author == user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None

def checkObjectForInvalidString(name,user,request):
    if name.isspace():
        return False,jsonErrorResponse(ERROR_MESSAGES['BLANKNAME'],request)
    if any(invalid in name for invalid in INVALIDCHARS):
        return False,jsonErrorResponse(ERROR_MESSAGES['INVALIDNAME'],request)
    return True,None

def _getFoldersAndFiles(folderobj,data={},printing=False,ident=''):
    data['name']=folderobj.name
    fileslist=[]
    folderslist=[]
    data['files']=fileslist
    data['folders']=folderslist
    #Hole TexFiles
    texfiles=TexFile.objects.filter(folder=folderobj)
    for f in texfiles:
        if printing:
            print('    ',f)
            print('     ',f.source_code)
        fileslist.append({'name':f.name,'bytes':str.encode(f.source_code)})
    
    #Hole Binary files
    #TODO

    #Füge rekursiv die Unterordner hinzu
    folders=Folder.objects.filter(parent=folderobj)

    for folder in folders:
        if printing:
            print(folder)
        folderslist.append(_getFoldersAndFiles(folder,data={},printing=printing,ident=ident+'    '))

    return data


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


def getProjectBytesFromProjectObject(projectobj):
    rootfolder=projectobj.rootFolder
    return _getFoldersAndFiles(rootfolder,printing=False)


def getFolderAndFileStructureAsDict(folderobj):
    return _getFoldersAndFilesJson(folderobj, data={})
