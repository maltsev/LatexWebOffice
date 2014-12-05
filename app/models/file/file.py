# -*- coding: utf-8 -*-
"""

* Purpose : Datei Modell (app/models/file/file.py)

* Creation Date : 20-11-2014

* Last Modified : 2 Dec 2014 21:31:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import io
import os
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
