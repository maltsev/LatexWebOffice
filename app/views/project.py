"""

* Purpose : Verwaltung von Project Models

* Creation Date : 19-11-2014

* Last Modified : Mi 03 Dez 2014 14:14:50 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : 2

* Backlog entry : TEK1, 3ED9, DOK8

"""

from django.http import HttpResponse, Http404
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.file import File
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.common import util
from app.common.constants import ERROR_MESSAGES, SUCCESS, FAILURE
import mimetypes, os, io, tempfile, zipfile, shutil, logging
from django.db import transaction



# erzeugt ein neues Projekt für den Benutzer mit einer leeren main.tex Datei
# benötigt: name:projectname
# liefert: HTTP Response (Json)
# Beispiel response: {'name': 'user1_project1', 'id': 1}
def projectCreate(request, user, projectname):
    # Teste, ob der Projektname kein leeres Wort ist (Nur Leerzeichen sind nicht erlaubt)
    # oder ungültige Sonderzeichen enthält
    emptystring, failurereturn = util.checkObjectForInvalidString(projectname, request)
    if not emptystring:
        return failurereturn

    # überprüfe ob ein Projekt mit dem Namen projectname bereits für diese Benutzer existiert
    if Project.objects.filter(name__iexact=projectname.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)
    else:
        try:
            newproject = Project.objects.create(name=projectname, author=user)
        except:
            return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)

    return util.jsonResponse({'id': newproject.id, 'name': newproject.name}, True, request)


# löscht ein vorhandenes Projekt eines Benutzers
# benötigt: id:projectid
# liefert: HTTP Response (Json)
def projectRm(request, user, projectid):
    # überprüfe ob das Projekt existiert und der user die Rechte zum Löschen hat
    rights, failurereturn = util.checkIfProjectExistsAndUserHasRights(projectid, user, request)
    # sonst gib eine Fehlermeldung zurück
    if not rights:
        return failurereturn

    # hole das zu löschende Projekt
    projectobj = Project.objects.get(id=projectid)

    # versuche das Projekt zu löschen
    try:
        projectobj.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


# liefert eine Übersicht aller Projekte eines Benutzers
# benötigt: nichts
# liefert: HTTP Response (Json)
# Beispiel response:
def listProjects(request, user):
    availableprojects = Project.objects.filter(author=user)

    if availableprojects is None:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [util.projectToJson(project) for project in availableprojects]

    return util.jsonResponse(json_return, True, request)


# importiert ein Projekt aus einer vom Client übergebenen zip Datei
# liefert: HTTP Response (Json)
def importZip(request, user):
    # Teste ob auch Dateien gesendet wurden
    if not request.FILES and not request.FILES.getlist('files'):
        return util.jsonErrorResponse(ERROR_MESSAGES['NOTALLPOSTPARAMETERS'], request)

    # Hole dateien aus dem request
    files = request.FILES.getlist('files')

    # Erstelle ein temp Verzeichnis, in welches die .zip Datei entpackt werden soll
    tmpfolder = tempfile.mkdtemp()

    zip_file_name=files[0].name

    # speichere die .zip Datei im tmp Verzeichnis
#    print(tmpfolder,files[0].name)
    zip_file_path = os.path.join(tmpfolder, files[0].name)
    zip_file = open(zip_file_path, 'wb')
    zip_file.write(files[0].read())
    zip_file.close()

    # überprüfe ob es sich um eine gültige .zip Datei handelt
    if not zipfile.is_zipfile(zip_file_path):
        return util.jsonErrorResponse(ERROR_MESSAGES['ILLEGALFILETYPE'], request)

    extract_path = os.path.join(tmpfolder, 'extracted')
    # erstelle einen Unterorder 'extracted'
    if not os.path.isdir(extract_path):
        os.mkdir(extract_path)

    # entpacke die .zip Datei in .../tmpfolder/extracted
    util.extractZipToFolder(extract_path, zip_file_path)

    fileName, fileExtension=os.path.splitext(zip_file_name)
    if Project.objects.filter(name__iexact=fileName.lower(),author=user).exists():
        Project.objects.get(name__iexact=fileName.lower(),author=user).delete()

    projectobj=Project.objects.create(name=fileName,author=user)

    # Lösche main.tex die vom Projekt angelegt wurde
    projectobj.rootFolder.getMainTex().delete()


    # objdictionary = []

    projdict={}

    parent=None
    folder=projectobj.rootFolder
    rootdepth=len(extract_path.split(os.sep))

    for root, dirs, files in os.walk(extract_path):
        path=root.split('/')[rootdepth:]
        #print('foldername',util.getFolderName(root))
        #print('parent',path[:-1])
        #print('parent2',os.path.join('',*path))
        if path:
            if path[:-1]:
                parent=projdict[os.path.join('',*path[:-1])]
            else:
                parent=projectobj.rootFolder
            folder=Folder.objects.create(name=util.getFolderName(root),parent=parent,root=projectobj.rootFolder)
            projdict[os.path.join('',*path)]=folder
        for f in files:
            fileobj=open(os.path.join(root,f),'rb')
            result,msg=util.uploadFile(fileobj,folder,request,True)
            fileobj.close()




    if os.path.isdir(tmpfolder):
        shutil.rmtree(tmpfolder)

    return util.jsonResponse({}, True, request)


# liefert ein vom Client angefordertes Projekt in Form einer zip Datei als Filestream
# benötigt: id:projectid
# liefert: filestream (404 im Fehlerfall)
def exportZip(request, user, projectid):
    # setze das logging level auf ERROR
    # da sonst Not Found: /document/ in der Console bei den Tests ausgegeben wird
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)

    # Überprüfe ob das Projekt, und der Benutzer die entsprechenden Rechte besitzt
    rights, failurereturn = util.checkIfProjectExistsAndUserHasRights(projectid, user, request)
    if not rights:
        raise Http404

    # setze das logging level wieder auf den ursprünglichen Wert
    logger.setLevel(previous_level)

    # hole das Projekt Objekt
    projectobj = Project.objects.get(id=projectid)

    # erstelle ein temp Verzeichnis mit einer Kopie des Projektes
    project_tmp_path = projectobj.rootFolder.dumpRootFolder()

    # tmp Verzeichnis in dem die zip Datei gespeichert wird
    zip_tmp_path = tempfile.mkdtemp()
    zip_file_path = os.path.join(zip_tmp_path, projectobj.name + '.zip')

    # erstelle die .zip Datei
    util.createZipFromFolder(project_tmp_path, zip_file_path)

    # lese die erstellte .zip Datei ein
    file_dl = open(zip_file_path, 'rb')
    response = HttpResponse(file_dl.read())
    file_dl.close()

    # lese die Dateigröße der zip Datei ein
    file_dl_size = str(os.stat(zip_file_path).st_size)

    # setze den mimetype
    ctype, encoding = mimetypes.guess_type(zip_file_path)

    if ctype is None:
        ctype = 'application/octet-stream'
    response['Content-Type'] = ctype
    response['Content-Length'] = file_dl_size
    if encoding is not None:
        response['Content-Encoding'] = encoding

    filename_header = 'filename=%s' % (projectobj.name + '.zip').encode('utf-8')

    response['Content-Disposition'] = 'attachment; ' + filename_header

    # lösche die temporären Dateien und Ordner
    if os.path.isdir(zip_tmp_path):
        shutil.rmtree(zip_tmp_path)

    return response


# gibt ein Projekt für einen anderen Benutzer zum Bearbeiten frei
# benötigt: id: projectid, name:inviteusername
# liefert HTTP Response (Json)
def shareProject(request, user, projectid, inviteusername):
    pass
