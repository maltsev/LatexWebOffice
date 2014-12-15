"""

* Purpose : Dokument- und Projektverwaltung Schnittstelle

* Creation Date : 19-11-2014

* Last Modified : Fr 12 Dez 2014 14:40:06 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8, DO14

"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from app.common import util
from app.common.constants import ERROR_MESSAGES
from app.views import file, folder, project, template
from django.shortcuts import render
from app.models.projecttemplate import ProjectTemplate
from app.models.file.file import File
from app.models.project import Project
from app.models.folder import Folder


def debug(request):
    return render(request, 'documentPoster.html')


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
            'projectcreate': {'command': project.projectCreate, 'parameters': [{'para': globalparas['name'], 'stringcheck':True}]},
            'projectrm': {'command': project.projectRm, 'parameters': [{'para': globalparas['id'], 'type':Project}]},
            'projectrename': {'command': project.projectRename, 'parameters': [{'para': globalparas['id'], 'type':Project}, {'para': globalparas['name'], 'stringcheck':True}]},
            'listprojects': {'command': project.listProjects, 'parameters': []},
            'importzip': {'command': project.importZip, 'parameters': []},
            'exportzip': {'command': project.exportZip, 'parameters': [{'para': globalparas['id']}]},
            'shareproject': {'command': project.shareProject, 'parameters': [{'para': globalparas['id'], 'type':Project}, {'para': globalparas['name'], 'stringcheck':True}]},
            'createtex': {'command': file.createTexFile, 'parameters': [{'para': globalparas['id'], 'type':Folder}, {'para': globalparas['name'], 'stringcheck':True}]},
            'updatefile': {'command': file.updateFile, 'parameters': [{'para': globalparas['id'], 'type':File}, {'para': globalparas['content']}]},
            'deletefile': {'command': file.deleteFile, 'parameters': [{'para': globalparas['id'], 'type':File}]},
            'renamefile': {'command': file.renameFile, 'parameters': [{'para': globalparas['id'], 'type':File}, {'para': globalparas['name'], 'stringcheck':True}]},
            'movefile': {'command': file.moveFile, 'parameters': [{'para': globalparas['id'], 'type':File}, {'para': globalparas['folderid'], 'type':Folder}]},
            'uploadfiles': {'command': file.uploadFiles, 'parameters': [{'para': globalparas['id'], 'type':Folder}]},
            'downloadfile': {'command': file.downloadFile, 'parameters': [{'para': globalparas['id']}]},
            'fileinfo': {'command': file.fileInfo, 'parameters': [{'para': globalparas['id'], 'type':File}]},
            'compile': {'command': file.latexCompile, 'parameters': [{'para': globalparas['id'], 'type':File}]},
            'createdir': {'command': folder.createDir, 'parameters': [{'para': globalparas['id'], 'type':Folder}, {'para': globalparas['name'], 'stringcheck':True}]},
            'rmdir': {'command': folder.rmDir, 'parameters': [{'para': globalparas['id'], 'type':Folder}]},
            'renamedir': {'command': folder.renameDir, 'parameters': [{'para': globalparas['id'], 'type':Folder}, {'para': globalparas['name'], 'stringcheck':True}]},
            'movedir': {'command': folder.moveDir, 'parameters': [{'para': globalparas['id'], 'type':Folder}, {'para': globalparas['folderid'], 'type':Folder}]},
            'listfiles': {'command': folder.listFiles, 'parameters': [{'para': globalparas['id'], 'type':Folder}]},
            'template2project': {'command': template.template2Project, 'parameters': [{'para': globalparas['id'], 'type':ProjectTemplate}, {'para': globalparas['name'], 'stringcheck':True}]},
            'project2template': {'command': template.project2Template, 'parameters': [{'para': globalparas['id'], 'type':Project}, {'para': globalparas['name'], 'stringcheck':True}]},
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
            if request.POST.get(para['para']['name']) is None:
                return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para['para']), request)
            elif para['para']['type'] == int and (not request.POST.get(para['para']['name']).isdigit()):
                return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format(para['para']), request)
            # sonst füge den Parameter zu der Argumentliste hinzu
            else:
                args.append(request.POST[para['para']['name']])

            # Teste auf ungültige strings
            if para.get('stringcheck'):
                failstring, failurereturn = util.checkObjectForInvalidString(
                    request.POST.get(para['para']['name']), request)
                if not failstring:
                    return failurereturn

            # Teste, dass der User rechte auf das Objekt mit der angegebenen id
            # hat und diese existiert
            if para.get('type') and para['para']['type']==int:
                objType=para.get('type')
                objId=request.POST.get(para['para']['name'])
                if objType==Project:
                    rights, failurereturn = util.checkIfProjectExistsAndUserHasRights(objId, user, request)
                    if not rights:
                        return failurereturn
                elif objType==Folder:
                    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(objId,user,request)
                    if not rights:
                        return failurereturn
                elif objType==File:
                    rights, failurereturn = util.checkIfFileExistsAndUserHasRights(objId,user,request)
                    if not rights:
                        return failurereturn
                elif objType==ProjectTemplate:
                    # Überprüfe, ob Vorlage existiert und der User darauf Rechte hat
                    emptystring, failurereturn = util.checkIfTemplateExistsAndUserHasRights(objId, user, request)
                    if not emptystring:
                        return failurereturn










        # führe den übergebenen Befehl aus
        return c['command'](request, user, *args)
    return util.jsonErrorResponse(ERROR_MESSAGES['MISSINGPARAMETER'].format('unkown'), request)
