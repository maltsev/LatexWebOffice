"""

* Purpose : Verwaltung von Project Models

* Creation Date : 19-11-2014

* Last Modified : Tu 17 Feb 2015 22:14:00 CET

* Author :  christian

* Coauthors : mattis, ingo, Kirill

* Sprintnumber : 2, 5

* Backlog entry : TEK1, 3ED9, DOK8, KOL1

"""

import os
import tempfile
import zipfile
import shutil
import logging

from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from app.models.collaboration import Collaboration
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
    """Liefert eine Übersicht aller Projekte eines Benutzers
       (einschließlich seiner kollaborativen Projekte).
    
    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :return: HttpResponse (JSON)
    """
    
    userprojects   = Project.objects.filter(author=user)
    collaborations = Collaboration.objects.filter(user=user,isConfirmed=True)
    
    if userprojects is None or collaborations is None:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [util.projectToJson(project)
                       for project in userprojects]
        json_return += [util.projectToJson(collaboration.project)
                        for collaboration in collaborations]
    
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


def inviteUser(request, user, projectid, inviteusermail):
    """Lädt einen anderen Benutzer zur Kollaboration an einem Projekt ein.
    
    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: ID des Projektes, zu dessen Zusammenarbeit eingeladen werden soll
    :param inviteusermail: E-Mail-Adresse des Benutzers, welcher eingeladen werden soll
    :return: HttpResponse (JSON)
    """
    
    # wenn sich die übergebene E-Mail-Adresse des einzuladenen Nutzers von der des aufrufenden Nutzers unterscheidet
    if user.username!=inviteusermail :
        # wenn die übergebene E-Mail-Adresse registriert ist
        if User.objects.filter(username=inviteusermail).exists() :
            # einzuladener Nutzer
            inviteuser = User.objects.get(username=inviteusermail)
            # wenn noch keine entsprechende Kollaboration vorliegt
            if not Collaboration.objects.filter(user=inviteuser.id,project=projectid).exists() :
                # versucht eine entsprechende Kollaboration anzulegen
                try:
                    Collaboration.objects.create(user=inviteuser, project=Project.objects.get(id=projectid))
                    return util.jsonResponse({}, True, request)
                except:
                    return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
            # wenn eine entsprechende Kollaboration bereits vorliegt
            else :
                return util.jsonErrorResponse(ERROR_MESSAGES['USERALREADYINVITED'].format(inviteusermail), request)
        else :
            return util.jsonErrorResponse(ERROR_MESSAGES['USERNOTFOUND'].format(inviteusermail), request)
    # wenn es sich bei der übergebenen E-Mail-Adresse des einzuladenen Nutzers um die des aufrufenden Nutzers handelt
    else :
        return util.jsonErrorResponse(ERROR_MESSAGES['USERALREADYINVITED'].format(inviteusermail), request)


def listInvitedUsers(request, user, projectid):
    """Liefert eine Liste der Nutzernamen aller Nutzer, welche für das, der übergebenen Projekt-ID entsprechende, Projekt eingeladen sind.
       Hierbei ist es unerheblich, ob die jeweilige Einladung bereits bestätigt wurde.
    
    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: ID des Projektes, von dessen eingeladenen Benutzern die Nutzernamen zurückgegeben werden sollen
    :return: HttpResponse (JSON)
    """
    
    collaborations = Collaboration.objects.filter(project=Project.objects.get(id=projectid))
    
    if collaborations is None:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [collaboration.user.username
                       for collaboration in collaborations]

    return util.jsonResponse(json_return, True, request)


def listUnconfirmedCollaborativeProjects(request, user):
    """Liefert eine Liste aller Projekte, zu deren Kollaboration der übergebene Benutzer eingeladen ist, diese jedoch noch nicht bestätigt hat.
    
    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :return: HttpResponse (JSON)
    """
    
    unconfirmedCollaborations = Collaboration.objects.filter(user=user,isConfirmed=False)
    
    if unconfirmedCollaborations is None:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [util.projectToJson(collaboration.project)
                       for collaboration in unconfirmedCollaborations]

    return util.jsonResponse(json_return, True, request)


def activateCollaboration(request, user, projectid):
    """Bestätigt der Einladung zur Kollaboration an einem Projekt.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: ID des Projektes, zu dessen die Einladung bestätigt werden soll
    :return: HttpResponse (JSON)
    """

    try:
        project = Project.objects.get(pk=projectid)
        collaboration = Collaboration.objects.get(user=user, project=project)
    except ObjectDoesNotExist:
        return util.jsonErrorResponse(ERROR_MESSAGES['COLLABORATIONNOTFOUND'], request)

    try:
        if not collaboration.isConfirmed:
            collaboration.isConfirmed = True
            collaboration.save()
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


    return util.jsonResponse({}, True, request)


def quitCollaboration(request, user, projectid):
    """Kündigt der Kollaboration (bzw. Einladung) an einem Projekt (als Kollaborator)

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: ID des Projektes, zu dessen die Kollaboration (bzw. die Einladung) gekündigt werden soll
    :return: HttpResponse (JSON)
    """

    try:
        project = Project.objects.get(pk=projectid)
        if user == project.author:
            return util.jsonErrorResponse(ERROR_MESSAGES['SELFCOLLABORATIONCANCEL'], request)

        collaboration = Collaboration.objects.get(user=user, project=project)
        collaboration.delete()
        return util.jsonResponse({}, True, request)
    except ObjectDoesNotExist:
        return util.jsonErrorResponse(ERROR_MESSAGES['COLLABORATIONNOTFOUND'], request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)



def cancelCollaboration(request, user, projectid, collaboratoremail):
    """Entzieht der Freigabe

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: ID des Projektes, zu dessen der Freigabe entzieht werden soll
    :param collaboratoremail: E-Mail-Adresse der Kollaborator
    :return: HttpResponse (JSON)
    """

    try:
        project = Project.objects.get(pk=projectid)
        collaborator = User.objects.get(username=collaboratoremail)
        if user == collaborator:
            return util.jsonErrorResponse(ERROR_MESSAGES['SELFCOLLABORATIONCANCEL'], request)

        collaboration = Collaboration.objects.get(user=collaborator, project=project)
        collaboration.delete()
    except ObjectDoesNotExist:
        return util.jsonErrorResponse(ERROR_MESSAGES['COLLABORATIONNOTFOUND'], request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)

    if not collaboration.isConfirmed:
        return util.jsonResponse({}, True, request)

    # Überprüfe ob ein Projekt mit gleichem Namen bereits für user existiert
    if Project.objects.filter(name__iexact=project.name.lower(), author=collaborator).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(project.name), request)

    try:
        Project.objects.cloneProject(project=project, author=collaborator)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


    return util.jsonResponse({}, True, request)