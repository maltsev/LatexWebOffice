"""

* Purpose : Verwaltung von Folder Models

* Creation Date : 19-11-2014

* Last Modified : Fr 12 Dez 2014 14:25:06 CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""
from app.models.folder import Folder
from app.common import util
from app.common.constants import ERROR_MESSAGES


def createDir(request, user, parentdirid=0, directoryname=""):
    """Erstellt einen neuen Ordner im angegebenen Verzeichnis.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param parentdirid: Id des übergeordneten Ordners
    :param directoryname: Name des zu erstellenden Ordners
    :return: HttpResponse (JSON)
    """

    # hole das übergeordnete Ordner Objekt
    parentdirobj = Folder.objects.get(id=parentdirid)

    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(directoryname, Folder, parentdirobj, request)
    if not unique:
        return failurereturn

    # Versuche den Ordner in der Datenbank zu speichern
    try:
        newfolder = Folder(name=directoryname, parent=parentdirobj, root=parentdirobj.getRoot())
        newfolder.save()
        return util.jsonResponse({'id': newfolder.id, 'name': newfolder.name, 'parentid': parentdirobj.id,
                                  'parentname': parentdirobj.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def rmDir(request, user, folderid):
    """Löscht den Ordner mit der angegebenen Id.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des zu löschenden Ordners
    :return: HttpResponse (JSON)
    """

    # hole das Ordner Objekt
    folderobj = Folder.objects.get(id=folderid)

    # überprüfe, ob der Ordner ein Rootfolder eines Projektes ist, diese dürfen nicht gelöscht werden
    if folderobj.isRoot():
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)

    # versuche das Ordner Objekt zu löschen
    try:
        folderobj.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def renameDir(request, user, folderid, newdirectoryname):
    """Benennt den Ordner mit der angegebenen Id um.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des Ordners, welcher umbenannt werden soll
    :param newdirectoryname: neuer Name des Ordners
    :return: HttpResponse (JSON)
    """

    # hole das Ordner Objekt
    folder = Folder.objects.get(id=folderid)

    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(newdirectoryname, Folder, folder.parent, request)
    if not unique:
        return failurereturn

    # Versuche die Änderung in die Datenbank zu übernehmen
    try:
        folder.name = newdirectoryname
        folder.save()
        return util.jsonResponse({'id': folder.id, 'name': folder.name}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def moveDir(request, user, folderid, newfolderid):
    """Verschiebt den Ordner mit der angegebenen id in den neuen Ordner mit der newfolderid.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des Ordners, der verschoben werden soll
    :param newfolderid: Id des Ordners, in welchen der Ordner mit der folderid verschoben werden soll
    :return: HttpResponse (JSON)
    """

    # hole die beiden Ordner Objekte
    folderobj = Folder.objects.get(id=folderid)
    newparentfolderobj = Folder.objects.get(id=newfolderid)

    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = util.checkIfFileOrFolderIsUnique(folderobj.name, Folder, newparentfolderobj, request)
    if not unique:
        return failurereturn

    # Versuche die Änderung in die Datenbank zu übernehmen
    try:
        # setze den newfolder als neues übergeordnetes Verzeichnis
        folderobj.parent = newparentfolderobj
        # dessen root Verzeichnis wird auch das Rootverzeichnis vom folderobj (verschieben zwischen Projekten)
        folderobj.root = newparentfolderobj.getRoot()
        folderobj.save()
        return util.jsonResponse({'id': folderobj.id,
                                  'name': folderobj.name,
                                  'parentid': folderobj.parent.id,
                                  'parentname': folderobj.parent.name,
                                  'rootid': folderobj.root.id},
                                 True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def listFiles(request, user, folderid):
    """Liefert eine Übersicht der Dateien/Unterordner eines Ordners (bzw. Projektes).

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param folderid: Id des Ordners, von dem die enthaltenen Dateien und Unterordner aufgelistet werden sollen
    :return: HttpResponse (JSON)
    """

    # hole das Ordner Objekt
    current_folderobj = Folder.objects.get(id=folderid)

    # erstelle die Ordner- und Dateistruktur als JSON
    folderandfiles_structure = util.getFolderAndFileStructureAsDict(current_folderobj)

    return util.jsonResponse(folderandfiles_structure, True, request)