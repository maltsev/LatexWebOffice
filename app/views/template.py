"""

* Purpose : Verwaltung von Folder Models

* Creation Date : 19-11-2014

* Last Modified : Mi 10 Dez 2014 13:27:20 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 2

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
        return util.jsonErrorResponse(ERROR_MESSAGES['TEMPLATEALREADYEXISTS'].format(projectname), request)

    # Erstelle Projekt aus der Vorlage
    template = ProjectTemplate.objects.get(id=vorlageid)
    project = Project.objects.createFromProjectTemplate(template)

    return util.jsonResponse({'id': project.id, 'name': project.name}, True, request)
