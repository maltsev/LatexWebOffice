# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 23-11-2014

* Last Modified : Mo 24 Nov 2014 12:23:46 CET

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
from app.models.file.document import Document
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
    elif not Project.objects.get(id=Folder.objects.get(id=folderid).getRootFolder().id).author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None

def checkIfFileExistsAndUserHasRights(fileid,user,request):
    if not File.objects.filter(id=fileid).exists():
        return False,jsonErrorResponse(ERROR_MESSAGES['FILENOTEXIST'],request)
    elif not File.objects.get(id=fileid).author==user:
        return False,jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'],request)
    else:
        return True,None
