""" 

* Purpose :

* Creation Date : 19-11-2014

* Last Modified : Do 20 Nov 2014 14:38:06 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import json


#@login_required
#@require_http_methods(['POST'])
def exportToPdf(request):
    """TODO: Docstring for exportToPdf.

    :request: A (POST) HttpRequest that has the following data: 
    texid: The id of the tex file
    content: The contents of the tex file
    :returns: TODO

    """
    #Get username
    user=request.user
    to_json={
                'status':'success',
                'message':'you failed',
                'content':None
             }

    if ('texid' in request.POST and 'content' in request.POST):
        texid=request.POST['texid']
        content=request.POST['content']


        #- Überprüfe, ob es diese Tex-Datei überhaupt gibt
        
        #Aktualisiere Tex Datei in der Datenbank

        #Zum Projekt der Tex-Datei dazugehörende Dateien abrufen

        #rueckgabe=Sende Dateien an Ingo's Methode

        #Falls rueckgabe okay -> sende pdf von Ingo an client

        #Sonst Fehlermeldung an Client
        to_json={
                'status':'success',
                'message':'you failed',
                'content':None
                }
    return HttpResponse(json.dumps(to_json),content_type="application/json")

