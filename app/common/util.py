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
