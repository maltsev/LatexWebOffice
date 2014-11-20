from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from app.models.project import Project
from django.template import Template, context, RequestContext

@login_required
def list(request):
    projects = Project.objects.all()
    return render_to_response('index.html', {'projects': projects}, context_instance=RequestContext(request))

@login_required
def editor(request, projectId):
    return HttpResponse("Project id: {}".format(projectId))