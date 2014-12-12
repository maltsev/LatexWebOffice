"""

* Purpose : Schnittstelle für Vorlagen

* Creation Date : 09-12-2014

* Last Modified : Fr 12 Dez 2014 14:02:24 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 3

* Backlog entry :  DO14

"""
from app.models.project import Project
from app.models.projecttemplate import ProjectTemplate
from app.common import util
from app.common.constants import ERROR_MESSAGES

# liefert HTTP Response (Json)
# Beispiel response: {}


def template2Project(request, user, vorlageid, projectname):

    # Überprüfe, ob Vorlage existiert und der User darauf Rechte hat
    emptystring, failurereturn = util.checkIfTemplateExistsAndUserHasRights(
        vorlageid, user, request)
    if not emptystring:
        return failurereturn

    # Überprüfe, ob der Projektname leer oder aus ungültigen Zeichen besteht
    emptystring, failurereturn = util.checkObjectForInvalidString(
        projectname, request)
    if not emptystring:
        return failurereturn

    # Überprüfe, ob es den Projektnamen schon gibt
    if Project.objects.filter(name__iexact=projectname.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['PROJECTALREADYEXISTS'].format(projectname), request)

    # Erstelle Projekt aus der Vorlage
    template = ProjectTemplate.objects.get(id=vorlageid)
    project = Project.objects.createFromProjectTemplate(
        template=template, name=projectname)

    return util.jsonResponse({'id': project.id, 'name': project.name}, True, request)


def project2Template(request, user, projectid, templatename):

    # Überprüfe, ob Projekt existiert und der User darauf Rechte hat
    emptystring, failurereturn = util.checkIfProjectExistsAndUserHasRights(
        projectid, user, request)
    if not emptystring:
        return failurereturn

    # Überprüfe, ob der Projektname leer oder aus ungültigen Zeichen besteht
    emptystring, failurereturn = util.checkObjectForInvalidString(
        templatename, request)
    if not emptystring:
        return failurereturn

    # Überprüfe, ob es den Vorlagenamen schon gibt
    if ProjectTemplate.objects.filter(name__iexact=templatename.lower(), author=user).exists():
        return util.jsonErrorResponse(ERROR_MESSAGES['TEMPLATEALREADYEXISTS'].format(templatename), request)

    # Erstelle template aus dem Project
    project = Project.objects.get(id=projectid)
    template = ProjectTemplate.objects.createFromProject(
        project=project, name=templatename)

    return util.jsonResponse({'id': template.id, 'name': template.name}, True, request)
