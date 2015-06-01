# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 23-11-2014

* Last Modified : Do 05 Mär 2015 13:03:04 CET

* Author :  christian

* Coauthors : mattis, ingo, Kirill

* Sprintnumber : -

* Backlog entry : -

"""

import simplejson as json
import zipfile
import os
import mimetypes
import tempfile
import re


from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

import settings
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE, INVALIDCHARS, MAXFILESIZE
from app.common.constants import DUPLICATE_NAMING_REGEX, DUPLICATE_INIT_SUFFIX_NUM
from app.common.allowedmimetypes import ALLOWEDMIMETYPES
from app.models.folder import Folder
from app.models.project import Project
from app.models.projecttemplate import ProjectTemplate
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.pdf import PDF
from app.models.collaboration import Collaboration


def jsonDecoder(responseContent):
    """Dekodiert ein JSON als Dictionary.

    :param responseContent: HttpResponse.content
    :return: dict
    """

    return json.loads(responseContent)


def jsonResponse(response, status, request):
    """Liefert HttpResponse (JSON).

    Dies ist die Standardmethode, um dem Client eine Antwort auf seine Anfragen zu schicken.

    :param response: Antwort, die gesendet werden soll
    :param status: Status der Antwort (True=success|False=failure)
    :param request: gesendete Anfrage des Clients, sollte unverändert zurückgeschickt werden
    :return: HttpResponse (JSON)
    """

    # setze den status der Antwort
    statusstr = FAILURE
    if status:
        statusstr = SUCCESS

    # Standardaufbau der Antwort des Servers für den Client
    to_json = {
        'status': statusstr,
        'request': request.POST,
        'response': response
    }

    return HttpResponse(json.dumps(to_json), content_type="application/json")


def jsonErrorResponse(errormsg, request):
    """Liefert HttpResponse (Json).

    Hilfsmethode, welche jsonResponse() aufruft, mit status=failure.

    :param errormsg: Fehlermeldung, welche dem Client gesendet werden soll
    :param request: gesendete Anfrage des Clients, sollte unverändert zurückgeschickt werden
    :return: HttpResponse (JSON)
    """

    return jsonResponse(errormsg, False, request)


def projectToJson(project):
    """Gibt die Daten eines Projektes|einer Vorlage als Dictionary zurück.

    :param project: Projekt|Vorlage als Objekt (Modell)
    :return: dict
    """

    projectdata = dict(id=project.id,
                       name=project.name,
                       ownerid=project.author.id,
                       ownername=project.author.username,
                       createtime=datetimeToString(project.createTime),
                       rootid=project.rootFolder.id)

    if isinstance(project, Project):
        projectdata["collaboratorsnum"] = len(project.getAllCollaborators())

    return projectdata


def checkIfDirExistsAndUserHasRights(folderid, user, request, requirerights, lockcheck=False):
    """Überprüft, ob der Ordner mit der folderid existiert, und der User die Rechte hat diesen zu bearbeiten.

    :param folderid: Id des Ordners, für welchen die Überprüfung durchgeführt werden soll
    :param user: Benutzer, für den die Überprüfung durchgeführt werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :param requirerights: Erforderte Rechte (z. B ['owner', 'collaborator'] — user soll der Autor ODER der Kollaborateur vom Projekt sein)
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    try:
        folder = Folder.objects.get(id=folderid)
        project = folder.getProject()
    except ObjectDoesNotExist:
        return False, jsonErrorResponse(ERROR_MESSAGES['DIRECTORYNOTEXIST'], request)

    if not isAllowedAccessToProject(project, user, requirerights):
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)

    if lockcheck:
        for file in folder.getFilesAndFoldersRecursively():
            if isinstance(file, File) and file.isLocked() and file.lockedBy() != user:
                return False, jsonErrorResponse(ERROR_MESSAGES['DIRLOCKED'], request)

    return True, None



def checkIfFileExistsAndUserHasRights(fileid, user, request, requirerights, lockcheck=False, objecttype=File):
    """Überprüft, ob die Datei mit der fileid existiert, und der User die Rechte hat diese zu bearbeiten.

    :param fileid: Id der Datei, für welche die Überprüfung durchgeführt werden soll
    :param user: Benutzer, für den die Überprüfung durchgeführt werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :param requirerights: Erforderte Rechte (z. B ['owner', 'collaborator'] — user soll der Autor ODER der Kollaborateur von der Datei sein)
    :param objecttype: Datei Objekt, für welches die Überprüfung durchgeführt werden soll, z.B. File oder TexFile
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    try:
        file = objecttype.objects.get(pk=fileid)
        project = file.folder.getRoot().getProject()
    except ObjectDoesNotExist:
        error = ERROR_MESSAGES['FILENOTEXIST']
        if not File.objects.filter(id=fileid).exists():
            return False, jsonErrorResponse(error, request)

        # wenn es eine Tex Datei sein soll, es sich aber um einen anderen Dateityp handelt
        if objecttype == TexFile:
            error = ERROR_MESSAGES['NOTEXFILE']
        elif objecttype == PlainTextFile:
            error = ERROR_MESSAGES['NOPLAINTEXTFILE']
        elif objecttype == PDF:
            error = ERROR_MESSAGES['NOPDFFILE']

        return False, jsonErrorResponse(error, request)

    if not isAllowedAccessToProject(project, user, requirerights):
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    elif lockcheck and file.isLocked() and file.lockedBy() != user:
        return False, jsonErrorResponse(ERROR_MESSAGES['FILELOCKED'], request)
    else:
        return True, None



def checkIfProjectExistsAndUserHasRights(projectid, user, request, requirerights):
    """Überprüft, ob das Projekt mit der projectid existiert, und der User die Rechte hat dieses zu bearbeiten.

    :param projectid: Id des Projektes, für welches die Überprüfung durchgeführt werden soll
    :param user: Benutzer, für den die Überprüfung durchgeführt werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :param requirerights: Erforderte Rechte (z. B ['owner', 'collaborator'] — user soll der Autor ODER der Kollaborateur vom Projekt sein)
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    try:
        project = Project.objects.get(pk=projectid)
    except ObjectDoesNotExist:
        return False, jsonErrorResponse(ERROR_MESSAGES['PROJECTNOTEXIST'], request)

    if isAllowedAccessToProject(project, user, requirerights):
        return True, None
    else:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)


def checkIfTemplateExistsAndUserHasRights(templateid, user, request):
    """Überprüft, ob die Vorlage mit der templateid existiert, und der User die Rechte hat diese zu bearbeiten.

    :param templateid: Id der Vorlage, für welche die Überprüfung durchgeführt werden soll
    :param user: Benutzer, für den die Überprüfung durchgeführt werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    if not ProjectTemplate.objects.filter(id=templateid, project__isnull=True).exists():
        return False, jsonErrorResponse(ERROR_MESSAGES['TEMPLATENOTEXIST'], request)
    elif not ProjectTemplate.objects.get(id=templateid).author == user:
        return False, jsonErrorResponse(ERROR_MESSAGES['NOTENOUGHRIGHTS'], request)
    else:
        return True, None


def checkIfFileOrFolderIsUnique(newname, modelClass, folder, request):
    """Überprüft ob eine Datei oder ein Ordner mit gleichem Namen bereits existiert.

    Diese Überprüfung ist case-insensitive, d.h. Groß- und Kleinschreibung wird dabei ignoriert.
    Beispiel: 'user1_project1' und 'USER1_Project1' werden als identisch betrachtet
    Achtung: Überprüfung funktioniert nicht mit SQLite, wenn der Name Nicht-ASCII Zeichen enthält (z.B. Umlaute)

    :param newname: Name, für den überprüft werden soll, ob bereits ein Objekt mit dem selben Namen existiert
    :param modelClass: File|Folder
    :param folder: Ordner, in welchem sich die Datei, bzw. der Ordner befindet
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    if modelClass == File:
        if File.objects.filter(name__iexact=newname.lower(), folder=folder).exists():
            return False, jsonErrorResponse(ERROR_MESSAGES['FILENAMEEXISTS'], request)
    else:
        if Folder.objects.filter(name__iexact=newname.lower(), parent=folder).exists():
            return False, jsonErrorResponse(ERROR_MESSAGES['FOLDERNAMEEXISTS'], request)
    return True, None


def checkObjectForInvalidString(string, request):
    """Überprüft, ob ein String ungültige Zeichen enthält.

    Ungültige Zeichen werden in der Konstanten INVALIDCHARS in /commom/constants.py festgelegt.

    :param string: String, welcher auf ungültige Zeichen überprüft werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    if string == '' or string.isspace():
        return False, jsonErrorResponse(ERROR_MESSAGES['BLANKNAME'], request)

    for invalid in INVALIDCHARS:
        if invalid in string:
            return False, jsonErrorResponse(ERROR_MESSAGES['INVALIDNAME'], request)

    return True, None


def checkFileForInvalidString(name, request):
    """Überprüft ob ein Dateiname ungültige Sonderzeichen enthält.

    :param name: Dateiname, welcher auf ungültige Zeichen überprüft werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgeschickt
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung), bzw. (True, None) bei Erfolg
    """

    # trenne die Dateiendung vom Dateinamen
    split_name = os.path.splitext(name)
    if split_name[0]:
        file_name, file_extension = split_name
    else:
        file_extension, file_name = split_name


    # file_extension ist ein leerer String wenn entweder keine Dateiendung vorhanden ist
    # oder der Dateiname nur die Dateiendung beinhaltet, z.B. name = '.tex'
    # wenn ein Dateiname ohne Dateiendung gesendet wurde, gib Fehlermeldung zurück
    if file_extension == '' and not (file_name.isspace() or file_name == ''):
        return False, jsonErrorResponse(ERROR_MESSAGES['INVALIDNAME'], request)

    return checkObjectForInvalidString(file_name, request)


def getFolderAndFileStructureAsDict(folderobj, user):
    """Liefert die Ordner- und Dateistruktur eines gegebenen Ordner Objektes als Dictionary.

    :param folderobj: Ordner Objekt, für den die gesamte Unterordner- und Dateistruktur geliefert werden soll
    :param user: User Objekt (eingeloggter Benutzer)
    :return: dict
    """

    return _getFoldersAndFilesJson(folderobj, user, data={'project': folderobj.getProject().name})


def _getFoldersAndFilesJson(folderobj, user, data={}):
    """Hilfsmethode zur rekursiven Bestimmung der Ordner- und Dateistruktur eines gegebenen Ordner Objektes.

    :param folderobj: Ordner Objekt, für den die gesamte Unterordner- und Dateistruktur geliefert werden soll
    :param user: User Objekt (eingeloggter Benutzer)
    :param data: Dictionary, in welchem die angeforderte Struktur gespeichert wird
    :return: dict
    """

    data['name'] = folderobj.name
    data['id'] = folderobj.id
    filelist = []
    folderlist = []
    data['files'] = filelist
    data['folders'] = folderlist

    # hole alle Dateien des aktuellen Ordner Objektes
    files = File.objects.filter(folder=folderobj)

    # durchlaufe alle Dateien im aktuellen Ordner Objekt (folderobj)
    for f in files:
        if not '<log>' in f.name:
            isAllowEdit = not f.isLocked() or f.lockedBy() == user
            filelist.append({'id': f.id, 'name': f.name, 'mimetype': f.mimeType, 'size': f.size,
                            'createTime': str(f.createTime), 'lastModifiedTime': str(f.lastModifiedTime), 'isAllowEdit': isAllowEdit})

    # hole alle Unterordner Objekte des aktuelle Ordner Objektes (folderobj)
    folders = Folder.objects.filter(parent=folderobj)

    # durchlaufe alle Unterordner im aktuellen Ordner Objekt
    for f in folders:
        # rufe diese Methode rekursiv mit dem Unterordner auf, und füge die Daten dem Dictionary hinzu
        folderlist.append(_getFoldersAndFilesJson(f, user, data={}))

    return data


def getMimetypeFromFile(python_file, file_name):
    """Liefert den Mimetype eines python files

    Voraussetzung: Datei existiert und es kann auf diese zugegriffen werden.

    :param python_file: python file Objekt
    :param file_name: Name der Datei
    :return: Mimetype der übergebenen Datei
    """

    # versuche den Mimetype mit Hilfe des python-magic wrappers zu bestimmen
    try:
        import magic
        # nutze das python-magic paket um den mimetype zu bestimmen
        mime_magic = magic.Magic(mime=True)
        # lese die ersten 1024 byte ein
        mimetype = mime_magic.from_buffer(python_file.read(1024)).decode('utf-8')
        # springe wieder zurück zum Anfang der Datei
        python_file.seek(0)
    # sollte dies nicht funktionieren, so nutze die Python Funktion zur Bestimmung des Mimetypes
    # diese Methode bestimmt den Mimetype nur aufgrund der Dateiendung, und ist dadruch nicht zuverlässing
    except:
        mimetype, encoding = mimetypes.guess_type(file_name)

    return mimetype


def getNextValidProjectName(user,name):
    """ Liefert anhand des übergebenen Namens einen Projektnamen, welcher für den angegebenen Benutzer noch nicht vorhanden ist.
        Hierbei wird dem übergebenen Namen ggf. ein Suffix der Form '(n)' angefügt,
        falls unter dem Projektnamen name bereits ein Projekt für den angegebenen Benutzer existiert.
    
    :param user: Benutzer, unter dessen Projekten ein noch nicht vorhandener Projektname ermittelt werden soll
    :param name: Name, anhand dessen ein noch nicht vorhandener Projektname ermittelt werden soll
    :return: name (unverändert), falls für den übergebenen Benutzer user noch kein Projekt mit diesem Namen vorhanden ist,
             andernfalls (unter dem Projektnamen name besteht für den Benutzer user bereits ein Projekt)
             wird eine Zeichenkette der Form name + ' (n)' zurückgegeben,
             wobei n eine Zahl, sodass noch kein entsprechendes Projekt mit diesem Namen für den Benutzer user vorhanden ist
    """
    
    # ermittelt alle Projekte von user, die mit name beginnen
    queryProjects = Project.objects.filter(author=user, name__istartswith=name)
    
    # wenn noch kein Projekt mit dem Namen name existiert, ...
    if not queryProjects.filter(name__iexact=name).exists() :
        # ... wird der übergebene Name name unverändert zurückgegeben
        return name
    # wenn bereits ein Projekt mit dem Namen name existiert, ...
    else :
        
        # ... wird über die natürlichen Zahlen (ab festgelegtem Startwert) iteriert
        n = DUPLICATE_INIT_SUFFIX_NUM
        while True :
            # wenn noch kein Projekt mit dem Namen name+' (n)' existiert, ...
            if not queryProjects.filter(name__iexact=DUPLICATE_NAMING_REGEX % (name,n)).exists() :
                # ... wird dieser zurückgegeben
                return DUPLICATE_NAMING_REGEX % (name,n)
            # wenn bereits ein Projekt mit dem Namen name+' (n)' existiert, ...
            else :
                # ... wird mit der nächsten Zahl fortgefahren
                n += 1


def getNextValidTemplateName(user,name):
    """ Liefert anhand des übergebenen Namens einen Vorlagennamen, welcher für den angegebenen Benutzer noch nicht vorhanden ist.
        Hierbei wird dem übergebenen Namen ggf. ein Suffix der Form '(n)' angefügt,
        falls unter dem Vorlagennamen name bereits eine Vorlage für den angegebenen Benutzer existiert.
    
    :param user: Benutzer, unter dessen Vorlagen ein noch nicht vorhandener Vorlagenname ermittelt werden soll
    :param name: Name, anhand dessen ein noch nicht vorhandener Vorlagenname ermittelt werden soll
    :return: name (unverändert), falls für den übergebenen Benutzer user noch keine Vorlage mit diesem Namen vorhanden ist,
             andernfalls (unter dem Vorlagennamen name besteht für den Benutzer user bereits eine Vorlage)
             wird eine Zeichenkette der Form name + ' (n)' zurückgegeben,
             wobei n eine Zahl, sodass noch keine entsprechende Vorlage mit diesem Namen für den Benutzer user vorhanden ist
    """
    
    # ermittelt alle Vorlagen von user, die mit name beginnen
    queryTemplates = ProjectTemplate.objects.filter(author=user, name__istartswith=name)
    
    # wenn noch keine Vorlage mit dem Namen name existiert, ...
    if not queryTemplates.filter(name__iexact=name).exists() :
        # ... wird der übergebene Name name unverändert zurückgegeben
        return name
    # wenn bereits eine Vorlage mit dem Namen name existiert, ...
    else :
        
        # ... wird über die natürlichen Zahlen (ab festgelegtem Startwert) iteriert
        n = DUPLICATE_INIT_SUFFIX_NUM
        while True :
            # wenn noch keine Vorlage mit dem Namen name+' (n)' existiert, ...
            if not queryTemplates.filter(name__iexact=DUPLICATE_NAMING_REGEX % (name,n)).exists() :
                # ... wird dieser zurückgegeben
                return DUPLICATE_NAMING_REGEX % (name,n)
            # wenn bereits eine Vorlage mit dem Namen name+' (n)' existiert, ...
            else :
                # ... wird mit der nächsten Zahl fortgefahren
                n += 1


def uploadFile(f, folder, request, fromZip=False):
    """Speichert eine hochgeladene Dateie als entsprechendes Objekt in der Datenbank.

    :param f: Datei welche in der Datenbank gespeichert werden soll (python file Objekt)
    :param folder: Ordner Objekt, in welchem die Datei gespeichert werden soll
    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param fromZip: True|False, je nachdem ob diese Methode von importzip() aufgerufen wurde oder nicht
    :return: (False, HttpResponse (JSON) mit der entsprechenden Fehlermeldung),
              bzw. (True, {'id': fileid, 'name': filename) bei Erfolg
    """

    # trenne den Dateinamen vom Dateipfad
    head, _name = os.path.split(f.name)

    # wandele den Dateiname nach 'utf-8' um, falls nötig
    name = convertLatinToUnicode(_name)

    # bestimme den Mimetype der Datei
    mime = getMimetypeFromFile(f, name)
    
    # speichere alte Position 
    old_file_position = f.tell()
    # gehe vom Anfang zum Ende
    f.seek(0, os.SEEK_END)
    # Speichere den Abstand vom Anfang zum Ende
    size = f.tell()
    # Gehere zurück zur alten Position in der Datei
    f.seek(old_file_position, os.SEEK_SET)

    if size > MAXFILESIZE:
        return False, ERROR_MESSAGES['MAXFILESIZE']




    # Überprüfe, ob die einzelnen Dateien einen Namen ohne verbotene Zeichen haben
    # und ob sie eine Dateiendung besitzen
    illegalstring, failurereturn = checkFileForInvalidString(name, request)
    if not illegalstring:
        return False, ERROR_MESSAGES['INVALIDNAME']

    # wenn die Datei leer ist (python-magic liefert hier 'application/x-empty'),
    # bestimme den Mimetype über die Dateiendung
    if mime == 'application/x-empty':
        mime, encoding = mimetypes.guess_type(name)

    # Überprüfe auf doppelte Dateien unter Nichtbeachtung Groß- und Kleinschreibung
    # Teste ob Ordnername in diesem Verzeichnis bereits existiert
    unique, failurereturn = checkIfFileOrFolderIsUnique(name, File, folder, request)
    if not unique:
        return False, ERROR_MESSAGES['FILENAMEEXISTS']

    # wenn der Mimetype eine erlaubte Binärdatei ist
    if mime in ALLOWEDMIMETYPES['binary']:
        if not fromZip:
            try:
                file = ALLOWEDMIMETYPES['binary'][mime].objects.createFromRequestFile(name=name, requestFile=f,
                                                                                      folder=folder, mimeType=mime)
            except:
                return False, ERROR_MESSAGES['DATABASEERROR']
        else:
            try:

                file = ALLOWEDMIMETYPES['binary'][mime].objects.createFromFile(name=name, file=f,
                                                                               folder=folder, mimeType=mime)
            except:
                return False, ERROR_MESSAGES['DATABASEERROR']
    # wenn der Mimetype eine erlaubte Plaintext Datei ist
    elif mime in ALLOWEDMIMETYPES['plaintext']:
        encoding = 'utf-8'
        try:
            import magic
            plaintextfile = f.read()
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(plaintextfile).decode(encoding='utf-8')
            f.seek(0)
        except:
            pass

        try:
            file = ALLOWEDMIMETYPES['plaintext'][mime].objects.create(name=name, source_code=f.read().decode(encoding),
                                                                      folder=folder, mimeType=mime)

            file.save()
        except:
            return False, ERROR_MESSAGES['DATABASEERROR']
    # sonst ist der Dateityp nicht erlaubt
    else:
        return False, ERROR_MESSAGES['ILLEGALFILETYPE'] % mime

    return True, {'id': file.id, 'name': file.name}


def createZipFromFolder(folderpath, zip_file_path):
    """Erstellt eine zip Datei des übergebenen Ordners inklusive aller Unterordner und zugehöriger Dateien.

    :param folderpath: Pfad zum Ordner, aus dem die .zip Datei erstellt werden soll, Beispiel: /home/user/test
    :param zip_file_path: Pfad zur .zip Datei, Beispiel: /home/user/test.zip
    :return: None
    """

    # sichere das aktuelle Arbeitsverzeichnis
    oldwd = os.getcwd()

    # wechsel das aktuelle Arbeitsverzeichnis (Verzeichnis der zip Datei)
    wd, _ = os.path.split(zip_file_path)
    os.chdir(wd)

    relroot = os.path.abspath(folderpath)

    zip = False
    try:
        zip = zipfile.ZipFile(zip_file_path, "w")
        for root, dirs, files in os.walk(folderpath):
            # füge des Verzeichnis hinzu (notwendig für Verzeichnisse ohne weitere Dateien und Unterordner)
            zip.writestr(str(os.path.relpath(root, relroot)) + os.path.sep, '')
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(str(filename), str(arcname))
    finally:
        if zip:
            zip.close()

    # stelle das vorherige Arbeitsverzeichnis wieder her
    os.chdir(oldwd)


def extractZipToFolder(folderpath, zip_file_path):
    """Entpackt alle Dateien und Ordner der zip Datei zip_file_path
       in den Ordner folderpath.

    :param folderpath: Pfad zum Ordner, in dem die .zip Datei entpackt
                       werden soll, Beispiel: /home/user/test
    :param zip_file_path: Pfad zur .zip Datei, Beispiel: /home/user/test.zip
    :return: None
    """

    zip_file = zipfile.ZipFile(zip_file_path, 'r')
    for name in zip_file.namelist():
        dirname, filename = os.path.split(name)

        if filename:
            # Datei
            fd = open(os.path.join(folderpath, name), 'w')
            fd.write(zip_file.read(name))
            fd.close()
        else:
            dirpath = os.path.join(folderpath, dirname)
            if not os.path.exists(dirpath):
                # Verzeichnis
                os.mkdir(dirpath)

    zip_file.close()


def getFileSize(pyfile):
    """Liefert die Dateigröße eines file objects in Bytes.

    funktioniert auch für StringIO Objekte

    :param pyfile: python file Objekt
    :return: Dateigröße in Bytes
    """

    old_file_position = pyfile.tell()
    pyfile.seek(0, os.SEEK_END)
    size = pyfile.tell()
    pyfile.seek(old_file_position, os.SEEK_SET)

    return size


def getFolderName(folderpath):
    """Gibt den Ordnernamen eines Ordnerpfades zurück.

    :param folderpath: kompletter Pfad des Ordners
    :return: Name des Ordners
    """

    path, folder_name = os.path.split(folderpath)

    return folder_name


def datetimeToString(date_time):
    """Gibt Zeit-Datum Objekt als String zurück.

    Format YYYY-MM-DD HH:MM:SS.MS+HH:MM

    :param date_time: Zeit-Datum Objekt
    :return: String
    """

    return str(date_time)


def getNewTempFolder():
    """Erstellt einen neuen temp Ordner im MEDIA_ROOT Verzeichnis und gibt den absoluten Pfad zurück.

    :return: Pfad zum erstellten temp Ordner
    """

    # Pfad in welchem der neue temp Ordner erstellt werden soll
    tmp_folder_path = os.path.join(settings.MEDIA_ROOT, 'tmp')

    # wenn der Ordner (temp_folder_path) noch nicht existiert
    if not os.path.isdir(tmp_folder_path):
        # erstelle den Ordner
        os.makedirs(tmp_folder_path)

    # erstelle im tmp_folder_path einen neuen temp Ordner
    tmp_folder = tempfile.mkdtemp(dir=tmp_folder_path)

    return tmp_folder


def convertLatinToUnicode(string):
    """Wandelt 'cp437' kodierte Strings in 'utf-8' um.

    Wird benötigt, da die python zipfile Bibliothek diese Kodierung für Dateinamen verwendet.

    :param string: String welcher von 'cp437' nach 'utf-8' konvertiert werden soll
    :return: 'utf-8'-kodierter String
    """

    # versuche den String nach 'utf-8' zu konvertieren
    try:
        return string.encode('cp437').decode('utf-8')
    # ansonsten gib den String unverändert zurück
    except UnicodeDecodeError:
        return string


# ----------------------------------------------------------------------------------------------------------------------
# Hilfsmethoden für Django Unit Tests

def _validateServerJsonResponse(self, responsecontent, status, response):
    """Prüft ob ein JSON korrekt zurückgeliefert wurde.

    (vgl. jsonResponse(response, status, request) )

    :param responsecontent: HttpResponse.content
    :param status: geforderter Status der Antwort (success|failure)
    :param response: geforderte Antwort des Servers
    :return: None
    """

    # dekodiere den JSON response als dictionary
    dictionary = jsonDecoder(responsecontent)

    # Prüfe ob status, request und response in der Antwort enhalten sind
    self.assertIn('status', dictionary)
    self.assertIn('request', dictionary)
    self.assertIn('response', dictionary)

    # Überprüfe, ob der status korrekt ist
    self.assertEqual(dictionary['status'], status)
    # Überprüfe, ob eine korrekte Antwort geliefert wurde
    self.assertEqual(dictionary['response'], response)


def validateJsonFailureResponse(self, responsecontent, errormsg):
    """Prüft ob ein JSON korrekt mit dem Status 'failure' und der richtigen Fehlermeldung zurückgeliefert wurde.

    (vgl. jsonResponse(response, status, request) )

    :param responsecontent: HttpResponse.content
    :param errormsg: geforderte Fehlermeldung des Servers
    :return: None
    """

    return _validateServerJsonResponse(self, responsecontent, FAILURE, errormsg)


def validateJsonSuccessResponse(self, responsecontent, response):
    """Prüft ob ein JSON korrekt mit dem Status 'success' und der richtigen Serverantwort zurückgeliefert wurde.

    (vgl. jsonResponse(response, status, request) )

    :param responsecontent: HttpResponse.content
    :param response: geforderte Antwort des Servers
    :return: None
    """

    return _validateServerJsonResponse(self, responsecontent, SUCCESS, response)


def documentPoster(self, command='NoCommand', idpara=None, idpara2=None, idpara3=None, idpara4=None, idpara5=None,
                   content=None, name=None, files=None):
    """Hilfsmethode um leichter die verschiedenen commands des document views durchzutesten.

    :param command: Befehl der ausgeführt werden soll
    :param idpara: Parameter id des auszuführenden Befehls
    :param idpara2: Parameter folderid des auszuführenden Befehls
    :param idpara3: Parameter formatid des auszuführenden Befehls
    :param content: Parameter content des auszuführenden Befehls
    :param name: Parameter name des auszuführenden Befehls
    :param files: Parameter files des auszuführenden Befehls
    :return: Anfrage an den Server mit den entsprechenden Daten
    """

    # Setze die passenden Parameter für die Anfrage an den Server
    dictionary = {'command': command}
    if idpara != None:
        dictionary['id'] = idpara
    if idpara2 != None:
        dictionary['folderid'] = idpara2
    if idpara3 != None:
        dictionary['formatid'] = idpara3
    if idpara4 != None:
        dictionary['compilerid'] = idpara4
    if idpara5 != None:
        dictionary['forcecompile'] = idpara5
    if content != None:
        dictionary['content'] = content
    if name != None:
        dictionary['name'] = name
    if files != None:
        dictionary['files'] = files

    # Sende Anfrage an den Server mit dem übergebenem Befehl und den zugehörigen Parametern
    return self.client.post('/documents/', dictionary)

def isSQLiteDatabse():
    return 'sqlite3' in settings.DATABASES['default']['ENGINE']


def isAllowedAccessToProject(project, user, requirerights):
    """Überprüft, ob der Benutzer mit requirerights darf das Projekt bearbeiten.

    :param project: das Projekt, für welches die Überprüfung durchgeführt werden soll
    :param user: Benutzer, für den die Überprüfung durchgeführt werden soll
    :param requirerights: Rechte des Benutzers
    :return: True or False
    """

    if 'collaborator' in requirerights and Collaboration.objects.filter(user=user, project=project, isConfirmed=True).exists():
        return True
    elif 'invitee' in requirerights and Collaboration.objects.filter(user=user, project=project, isConfirmed=False).exists():
        return True
    elif 'owner' in requirerights and project.author == user:
        return True
    else:
        return False



def unescapeHTML(s):
    """Dekodiert HTML-Zeichen. Verbesserte Variante von HTMLParser.HTMLParse.unescape() (Python 2.4)
    Quelle: https://hg.python.org/cpython/file/2.7/Lib/HTMLParser.py#l447

    :param s: Zeichenkette mit HTML-Zeichen
    :return: String
    """

    if '&' not in s:
        return s
    def replaceEntities(s):
        s = s.groups()[0]
        try:
            if s[0] == "#":
                s = s[1:]
                if s[0] in ['x','X']:
                    c = int(s[1:], 16)
                else:
                    c = int(s)
                return unichr(c)
        except ValueError:
            return '&#'+s+';'
        else:
            # Cannot use name2codepoint directly, because HTMLParser supports apos,
            # which is not part of HTML 4
            import htmlentitydefs
            if unescapeHTML.entitydefs is None:
                unescapeHTML.entitydefs = {'apos':u"'"}
                for k, v in htmlentitydefs.name2codepoint.iteritems():
                    unescapeHTML.entitydefs[k] = unichr(v)
            try:
                return unescapeHTML.entitydefs[s]
            except KeyError:
                return '&'+s+';'

    return re.sub(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));", replaceEntities, s)

unescapeHTML.entitydefs = None