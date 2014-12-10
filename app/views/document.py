"""

* Purpose : Dokument- und Projektverwaltung Schnittstelle

* Creation Date : 19-11-2014

* Last Modified : Do 04 Dez 2014 14:56:39 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from app.common import util
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
from django.conf import settings
from app.views import file, folder, project
from django.http import HttpResponse, Http404


# Schnittstellenfunktion
# bietet eine Schnittstelle zur Kommunikation zwischen Client und Server
# liest den vom Client per POST Data übergebenen Befehl ein
# und führt die entsprechende Methode aus
@login_required
@require_http_methods(['POST'])
def execute(request):
    if request.method == 'POST' and 'command' in request.POST:

        # hole den aktuellen Benutzer
        user = request.user

        globalparas = {'id': {'name': 'id', 'type': int}, 'content': {'name': 'content', 'type': str},
                       'folderid': {'name': 'folderid', 'type': int}, 'name': {'name': 'name', 'type': str},
                       'formatid': {'name': 'formatid', 'type': int}}

        # dictionary mit verfügbaren Befehlen und den entsprechenden Aktionen
        # die entsprechenden Methoden befinden sich in:
        # '/app/views/project.py', '/app/views/file.py' und '/app/views/folder.py'
        available_commands = {
            'projectcreate': {'command': project.projectCreate, 'parameters': (globalparas['name'],)},
            'projectrm': {'command': project.projectRm, 'parameters': (globalparas['id'],)},
            'listprojects': {'command': project.listProjects, 'parameters': ()},
            'importzip': {'command': project.importZip, 'parameters': ()},
            'exportzip': {'command': project.exportZip, 'parameters': (globalparas['id'],)},
            'shareproject': {'command': project.shareProject, 'parameters': (globalparas['id'], globalparas['name'])},
            'createtex': {'command': file.createTexFile, 'parameters': (globalparas['id'], globalparas['name'])},
            'updatefile': {'command': file.updateFile, 'parameters': (globalparas['id'], globalparas['content'])},
            'deletefile': {'command': file.deleteFile, 'parameters': (globalparas['id'],)},
            'renamefile': {'command': file.renameFile, 'parameters': (globalparas['id'], globalparas['name'])},
            'movefile': {'command': file.moveFile, 'parameters': (globalparas['id'], globalparas['folderid'])},
            'uploadfiles': {'command': file.uploadFiles, 'parameters': (globalparas['id'],)},
            'downloadfile': {'command': file.downloadFile, 'parameters': (globalparas['id'],)},
            'fileinfo': {'command': file.fileInfo, 'parameters': (globalparas['id'],)},
            'compile': {'command': file.latexCompile, 'parameters': (globalparas['id'],)},
            'createdir': {'command': folder.createDir, 'parameters': (globalparas['id'], globalparas['name'])},
            'rmdir': {'command': folder.rmDir, 'parameters': (globalparas['id'],)},
            'renamedir': {'command': folder.renameDir, 'parameters': (globalparas['id'], globalparas['name'])},
            'movedir': {'command': folder.moveDir, 'parameters': (globalparas['id'], globalparas['folderid'])},
            'listfiles': {'command': folder.listFiles, 'parameters': (globalparas['id'],)},
        }

        # wenn der Schlüssel nicht gefunden wurde
        # gib Fehlermeldung zurück
        if request.POST['command'] not in available_commands:
            return util.jsonErrorResponse(ERROR_MESSAGES['COMMANDNOTFOUND'], request)

        args = []

        # aktueller Befehl
        c = available_commands[request.POST['command']]
        # Parameter dieses Befehls
        paras = c['parameters']

        # durchlaufe alle Parameter des Befehls
        for para in paras:
            # wenn der Parameter nicht gefunden wurde oder ein Parameter, welcher eine id angeben sollte
            # Zeichen enthält, die keine Zahlen sind, gib Fehlermeldung zurück
            if request.POST.get(para['name'])==None:
                return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para), request)
            elif para['type'] == int and (not request.POST.get(para['name']).isdigit()):
                return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para), request)
            # sonst füge den Parameter zu der Argumentliste hinzu
            else:
                args.append(request.POST[para['name']])

        # führe den übergebenen Befehl aus
        return c['command'](request, user, *args)
    return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format('unkown'),request)
