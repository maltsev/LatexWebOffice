"""

* Purpose : Schnittstelle für Vorlagen

* Creation Date : 09-12-2014

* Last Modified : Fri 12 Dec 2014 07:55:30 PM CET

* Author :  mattis

* Coauthors : christian

* Sprintnumber : 3, 4

* Backlog entry :  DO14

"""
from app.models.project import Project
from app.models.projecttemplate import ProjectTemplate
from app.common import util
from app.common.constants import ERROR_MESSAGES


def template2Project(request, user, templateid, projectname):
    """Wandelt eine Vorlage in ein Projekt um.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param templateid: Id der Vorlage, welche umgewandelt werden soll
    :param projectname: Name des zu erstellenden Projektes
    :return: HttpResponse (JSON)
    """

    # Überprüfe, ob es den Projektnamen schon gibt
    if Project.objects.filter(name__iexact=projectname.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)

    # Erstelle Projekt aus der Vorlage
    template = ProjectTemplate.objects.get(id=templateid)
    project = Project.objects.createFromProjectTemplate(
        template=template, name=projectname)

    return util.jsonResponse({'id': project.id, 'name': project.name, 'rootid': project.rootFolder.id}, True, request)


def project2Template(request, user, projectid, templatename):
    """Wandelt ein Projekt in eine Vorlage um.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param projectid: Id des Projektes, welches umgewandelt werden soll
    :param templatename: Name der zu erstellenden Vorlage
    :return: HttpResponse (JSON)
    """

    # Überprüfe, ob es den Vorlagenamen schon gibt
    if ProjectTemplate.objects.filter(name__iexact=templatename.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['TEMPLATEALREADYEXISTS'].format(templatename), request)

    # Erstelle template aus dem Project
    project = Project.objects.get(id=projectid)
    template = ProjectTemplate.objects.createFromProject(project=project, name=templatename)

    return util.jsonResponse({'id': template.id, 'name': template.name}, True, request)


def templateRm(request, user, templateid):
    """Löscht eine vorhandene Vorlage.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param templateid: Id der Vorlage welche gelöscht werden soll
    :return: HttpResponse (JSON)
    """

    # hole die zu löschende Vorlage
    templateobj = ProjectTemplate.objects.get(id=templateid)

    # versuche die Vorlage zu löschen
    try:
        templateobj.delete()
        return util.jsonResponse({}, True, request)
    except:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def templateRename(request, user, templateid, newtemplatename):
    """Benennt eine Vorlage um.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :param templateid: Id der Vorlage welche umbenannt werden soll
    :param newtemplatename: neuer Name der Vorlage
    :return: HttpResponse (JSON)
    """

    # hole die Vorlage, welche umbenannt werden soll
    templateobj = ProjectTemplate.objects.get(id=templateid)

    # überprüfe ob eine Vorlage mit dem Namen 'newtemplatename' bereits für diese Benutzer existiert
    if ProjectTemplate.objects.filter(name__iexact=newtemplatename.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['TEMPLATEALREADYEXISTS'].format(newtemplatename), request)
    else:
        # versuche die Vorlage umzubenennen
        try:
            templateobj.name = newtemplatename
            templateobj.save()
            return util.jsonResponse({'id': templateobj.id, 'name': templateobj.name}, True, request)
        except:
            return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)


def listTemplates(request, user):
    """Liefert eine Übersicht aller Vorlagen eines Benutzers.

    :param request: Anfrage des Clients, wird unverändert zurückgesendet
    :param user: User Objekt (eingeloggter Benutzer)
    :return: HttpResponse (JSON)
    """

    availableprojects = ProjectTemplate.objects.filter(author=user).exclude(project__isnull=False)

    if availableprojects is None:
        return util.jsonErrorResponse(ERROR_MESSAGES['DATABASEERROR'], request)
    else:
        json_return = [util.projectToJson(template)
                       for template in availableprojects]

    return util.jsonResponse(json_return, True, request)