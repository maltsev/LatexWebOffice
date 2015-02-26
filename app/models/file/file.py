# -*- coding: utf-8 -*-
"""

* Purpose : Datei Modell (app/models/file/file.py)

* Creation Date : 20-11-2014

* Last Modified : Do 26 Feb 2015 13:33:53 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import io
import os

from django.db import models
from django.contrib.auth.models import User

from django.conf import settings

class FileManager(models.Manager):
    def clone(self, fileModel, **kwargs):
        defaultArgs = {
            'name': fileModel.name,
            'folder': fileModel.folder
        }
        args = dict(list(defaultArgs.items()) + list(kwargs.items()))
        return fileModel.__class__.objects.create(**args)


class File(models.Model):
    name = models.CharField(max_length=255)  # Dateiname (z.B. readme.tex)
    createTime = models.DateTimeField(auto_now_add=True)
    lastModifiedTime = models.DateTimeField(auto_now=True)
    folder = models.ForeignKey("Folder")
    mimeType = models.CharField(max_length=255, default='application/octet-stream')
    size = models.PositiveIntegerField(default=0)
    lasteditor = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True)
    objects = FileManager()

    class Meta:
        unique_together = ('name', 'folder')


    def getContent(self):
        return io.StringIO()

    ##
    # Abbildet die Datei auf der Festplatte und gibt den temporären Verzeichnispfad zurück
    # @return String
    def getTempPath(self):
        fileContentObj = self.getContent()
        if hasattr(fileContentObj, 'getvalue') and callable(fileContentObj.getvalue):
            fileContent = fileContentObj.getvalue().encode("utf-8")
        else:
            fileContent = fileContentObj.read()

        fileTempPath = os.path.join(self.folder.getTempPath(), self.name)
        if not os.path.exists(fileTempPath):
            file = open(fileTempPath, 'wb')
            file.write(fileContent)
            file.close()

        return fileTempPath


    def __str__(self):
        return "{}{}".format(self.folder, self.name)
