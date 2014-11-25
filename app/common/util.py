# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 23-11-2014

* Last Modified : Tue 25 Nov 2014 09:47:04 PM CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : -

* Backlog entry : -

"""

from django.http import HttpResponse
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
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
    elif not File.objects.get(id=fileid).folder.getProject().author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None

def checkObjectForEmptyString(name,user,request):
    if not name.strip():
        return False,jsonErrorResponse(ERROR_MESSAGES['BLANKNAME'],request)
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
        fileslist.append({'file':{'name':f.name,'bytes':str.encode(f.source_code)}})
    
    #Hole Binary files
    #TODO

    #Füge rekursiv die Unterordner hinzu
    folders=Folder.objects.filter(parent=folderobj)

    for folder in folders:
        if printing:
            print(folder)
        folderslist.append({'folder':_getFoldersAndFiles(folder,data={},printing=printing,ident=ident+'    ')})

    return data


def getProjectBytesFromProjectObject(projectobj):
    rootfolder=projectobj.rootFolder
    return _getFoldersAndFiles(rootfolder,printing=False)
    
    
