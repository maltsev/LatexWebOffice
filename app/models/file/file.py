# -*- coding: utf-8 -*-
import io
from django.db import models

class File(models.Model):
    name = models.CharField(max_length=255) # Dateiname (z.B. readme.tex)
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifiedTime = models.DateTimeField(auto_now=True)
    folder = models.ForeignKey("Folder")

    class Meta:
        unique_together = ('name', 'folder')


    def getContent(self):
        return io.StringIO()

    def __str__(self):
        return self.name
