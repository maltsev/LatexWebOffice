# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from app.models import folder


class File(models.Model):
    name = models.CharField(max_length=255) # Dateiname (z.B. readme.tex)
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifiedTime = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User)
    folder = models.ForeignKey(folder.Folder)

    class Meta:
        abstract = True
        unique_together = ('name', 'folder')

    def __str__(self):
        return self.name