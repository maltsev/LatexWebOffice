"""

* Purpose : Verwaltung von Project Models

* Creation Date : 19-11-2014

* Last Modified : Thu 22 Jan 2015 11:10:45 AM CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""

import os
import tempfile
import zipfile
import shutil
import logging

from django.http import HttpResponse, Http404
from django.db import transaction

from app.models.folder import Folder
from app.models.project import Project
from app.common import util
from app.common.constants import ERROR_MESSAGES, ZIPMIMETYPE, STANDARDENCODING


def projectCreate(request, user, projectname):
    """Erstellt ein neues Projekt mit dem Namen 'projectname'.

    Es wird ein neues Projekt in der Datenbank angelegt.
    Durch das Projektmodell wird automatisch eine leere main.tex Datei im Hauptverzeichnis erstellt.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectname: Name des neuen Projektes
    :return: HttpResponse (JSON)
    """

    # überprüfe ob ein Projekt mit dem Namen 'projectname' bereits für diese Benutzer existiert
    if Project.objects.filter(name__iexact=projectname.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)
    else:
        # versuche das Projekt in der Datenbank zu erstellen
        try:
            newproject = Project.objects.create(name=projectname, author=user)
        except:
            return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)

    # gib die Id und den Namen des erstellte Projektes zurück
    return util.jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)


def projectClone(request, user, projectid, newprojectname):
    """Erstellt eine Kopie eines Projektes mit dem Namen newprojectname

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: Id des Projektes, welches geklont werden soll
    :param newprojectname: Name des neuen Projektes
    :return: HttpResponse (JSON)
    """

    # überprüfe ob ein Projekt mit dem Namen 'projectname' bereits für diese Benutzer existiert
    if Project.objects.filter(name__iexact=newprojectname.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(newprojectname), request)
    else:
        # hole des aktuelle Projekt Objekt
        projectobj = Project.objects.get(id=projectid, author=user)

        # versuche das Projekt in der Datenbank zu erstellen
        try:
            newproject = Project.objects.cloneProject(project=projectobj, name=newprojectname)
        except:
            return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)

    # gib die Id und den Namen des erstellte Projektes zurück
    return util.jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)

def projectRm(request, user, projectid):
    """Löscht ein vorhandenes Projekt eines Benutzers.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: Id des Projektes welches gelöscht werden soll
    :return: HttpResponse (JSON)
    """

    # hole das zu löschende Projekt
    projectobj = Project.objects.get(id=projectid)

    # versuche das Projekt zu löschen
    try:
        projectobj.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def projectRename(request, user, projectid, newprojectname):
    """Benennt ein Projekt um.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: Id des Projektes welches umbenannt werden soll
    :param newprojectname: neuer Name des Projektes
    :return: HttpResponse (JSON)
    """

    # hole das Projekt, welches umbenannt werden soll
    projectobj = Project.objects.get(id=projectid)
    # überprüfe ob ein Projekt mit dem Namen 'projectname' bereits für diese Benutzer existiert
    if Project.objects.filter(name__iexact=newprojectname.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(newprojectname), request)
    else:
        # versuche das Projekt umzubenennen
        try:
            projectobj.name = newprojectname
            projectobj.save()
            return util.jsonResponse({'id': projectobj.id, 'name': projectobj.name}, True, request)
        except:
            return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def listProjects(request, user):
    """Liefert eine Übersicht aller Projekte eines Benutzers.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :return: HttpResponse (JSON)
    """

    availableprojects = Project.objects.filter(author=user)

    if availableprojects is None:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [util.projectToJson(project)
                       for project in availableprojects]

    return util.jsonResponse(json_return, True, request)


def importZip(request, user):
    """Importiert ein Projekt aus einer vom Client übergebenen zip Datei.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :return: HttpResponse (JSON)
    """

    # Teste ob auch Dateien gesendet wurden
    if not request.FILES and not request.FILES.getlist('files'):
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTALLPOSTPARAMETERS'], request)

    # Hole dateien aus dem request
    files = request.FILES.getlist('files')

    # Erstelle ein temp Verzeichnis, in welches die .zip Datei entpackt werden soll
    tmpfolder = util.getNewTempFolder()

    zip_file_name = files[0].name

    # speichere die .zip Datei im tmp Verzeichnis
    zip_file_path = os.path.join(tmpfolder, zip_file_name)
    zip_file = open(zip_file_path, 'wb')
    zip_file.write(files[0].read())
    zip_file.close()

    # überprüfe ob es sich um eine gültige .zip Datei handelt
    # und ob die zip Datei kleiner als 150 bytes ist
    # zip Datei ohne Inhalt ist 105 bytes gross
    if not os.path.getsize(zip_file_path) > 105 :
        return util.jsonErrorResponse(ERROR_MESSAGES['EMPTYZIPFILE'],request)
    if not zipfile.is_zipfile(zip_file_path) :
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTAZIPFILE'], request)

    extract_path = os.path.join(tmpfolder, 'extracted')
    # erstelle einen Unterorder 'extracted'
    if not os.path.isdir(extract_path):
        os.mkdir(extract_path)

    # entpacke die .zip Datei in .../tmpfolder/extracted
    util.extractZipToFolder(extract_path, zip_file_path)

    # benutze den Namen der zip Datei (ohne Dateiendung) als Projektnamen
    project_name, fileExtension = os.path.splitext(zip_file_name)


    # Erstelle das neue Projekt mit einen Namen, welcher ungültig ist.
    projectobj = Project.objects.create(name=project_name + '<old', author=user)

    # Lösche main.tex die vom Projekt angelegt wurde
    projectobj.rootFolder.getMainTex().delete()

    # dictionary in der als keyword der Pfad und als value ein Folder objekt gespeichert werden soll.
    # Dies soll dafür sorgen, dass wir später ohne probleme das
    # Elternverzeichnis eines Verzeichnis herausfinden können
    projdict = {}

    parent = None
    folder = projectobj.rootFolder

    # Tiefe des Verzeichnis, wo die zip entpackt wurde
    rootdepth = len(extract_path.split(os.sep))

    # durchlaufe alle Ordner/Unterordner in extracted
    # und erstelle die jeweiligen Objekte in der Datenbank
    # Dateien werden über die util.uploadfiles() Methode erstellt
    returnmsg = util.jsonResponse({'id': projectobj.id, 'name': project_name, 'rootid': projectobj.rootFolder.id}, True,
                                  request)

    failed = False

    try:
        with transaction.atomic():
            for root, dirs, files in os.walk(extract_path):
                # relativer Pfad des derzeitigen Verzeichnis
                path = root.split(os.sep)[rootdepth:]
                # falls path true ist, ist root nicht das root Verzeichnis, wo die zip
                # entpackt wurde
                if path:
                    # path is also ein subsubfolder und wir müssen den subfolder als parent setzen
                    if path[:-1]:
                        parent = projdict[os.path.join('', *path[:-1])]
                    else:
                        parent = projectobj.rootFolder
                    name = util.convertLatinToUnicode(util.getFolderName(root))
                    if name == '__MACOSX':
                        continue
                    # speichere Ordner
                    folder = Folder.objects.create(
                        name=util.convertLatinToUnicode(util.getFolderName(root)),
                        parent=parent, root=projectobj.rootFolder)
                    projdict[os.path.join('', *path)] = folder
                for f in files:  # füge die Dateien dem Ordner hinzu
                    fileobj = open(os.path.join(root, f), 'rb')
                    result, msg = util.uploadFile(fileobj, folder, request, True)
                    fileobj.close()
                    if not result:
                        returnmsg = util.jsonErrorResponse(msg, request)
                        raise TypeError
    except TypeError:
        projectobj.delete()  # bei Fehler muss noch das Projekt selbst gelöscht werden
        failed = True

    if not failed:
        # prüfe ob ein Projekt mit dem gleichen Namen bereits existiert
        # Groß- und Kleinschreibung wird hierbei nicht beachtet
        # wenn es existiert, dann lösche dies
        # Achtung: Projekt wird ohne weitere Abfrage komplett gelöscht
        # Es ist Aufgabe des Clients, vorher eine Abfrage anzuzeigen
        if Project.objects.filter(name__iexact=project_name.lower(), author=user).exists():
            Project.objects.get(name__iexact=project_name.lower(), author=user).delete()
        projectobj.name = project_name
        projectobj.save()


    # lösche alle temporären Dateien und Ordner
    if os.path.isdir(tmpfolder):
        shutil.rmtree(tmpfolder)
    return returnmsg


def exportZip(request, user, folderid):
    """Liefert ein vom Client angefordertes Projekt in Form einer zip Datei als Filestream.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des Ordners, welcher als zip Datei exportiert werden soll (rootId für komplettes Projekt)
    :return: filestream (404 im Fehlerfall)
    """

    # setze das logging level auf ERROR
    # da sonst Not Found: /document/ in der Console bei den Tests ausgegeben wird
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)

    # Überprüfe ob das Projekt, und der Benutzer die entsprechenden Rechte besitzt
    rights, failurereturn = util.checkIfDirExistsAndUserHasRights(
        folderid, user, request)
    if not rights:
        raise Http404

    # setze das logging level wieder auf den ursprünglichen Wert
    logger.setLevel(previous_level)

    folderobj = Folder.objects.get(id=folderid)

    # erstelle ein temp Verzeichnis mit einer Kopie des Ordners
    folder_tmp_path = folderobj.dumpFolder()

    if folderobj.isRoot():
        zip_file_name = folderobj.getProject().name + '.zip'
    else:
        zip_file_name = folderobj.name + '.zip'

    # tmp Verzeichnis in dem die zip Datei gespeichert wird
    zip_tmp_path = tempfile.mkdtemp()
    zip_file_path = os.path.join(zip_tmp_path, zip_file_name)

    # erstelle die .zip Datei
    util.createZipFromFolder(folder_tmp_path, zip_file_path)

    # lese die erstellte .zip Datei ein
    file_dl = open(zip_file_path, 'rb')
    response = HttpResponse(file_dl.read())
    file_dl.close()

    # lese die Dateigröße der zip Datei ein
    file_dl_size = str(os.stat(zip_file_path).st_size)

    response['Content-Type'] = ZIPMIMETYPE
    response['Content-Length'] = file_dl_size
    response['Content-Encoding'] = STANDARDENCODING

    filename_header = 'filename=%s' % ('\"' + zip_file_name + '\"')

    response['Content-Disposition'] = 'attachment; ' + filename_header

    # lösche die temporären Dateien und Ordner
    if os.path.isdir(zip_tmp_path):
        shutil.rmtree(zip_tmp_path)
    if os.path.isdir(folder_tmp_path):
        shutil.rmtree(folder_tmp_path)

    return response


# gibt ein Projekt für einen anderen Benutzer zum Bearbeiten frei
# benötigt: id: projectid, name:inviteusername
# liefert HTTP Response (Json)
def shareProject(request, user, projectid, inviteusername):
    pass
