# -*- coding: utf-8 -*-
from django.db import models
from app.models import folder


class File(models.Model):
    name = models.CharField(max_length=255) # Dateiname (z.B. readme.tex)
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifiedTime = models.DateTimeField(auto_now=True)
    folder = models.ForeignKey(folder.Folder)

    class Meta:
        unique_together = ('name', 'folder')

    def __str__(self):
        return self.name