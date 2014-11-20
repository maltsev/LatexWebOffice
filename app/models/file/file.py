# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from app.models.project import Project


class File(models.Model):
    name = models.CharField(max_length=255) # Dateiname (z.B. readme.tex)
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifiedTime = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User)
    project = models.ForeignKey(Project)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name