# -*- coding: utf-8 -*-
"""

* Purpose : Textdatei Modell (app/models/file/plaintextfile.py)

* Creation Date : 26-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import StringIO

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from app.models.file import file
from app.common.constants import SEEK_END, SEEK_SET


class PlainTextFileManager(file.FileManager):
    def clone(self, plainTextFileModel, **kwargs):
        defaultArgs = {
            'source_code': plainTextFileModel.source_code
        }
        args = dict(list(defaultArgs.items()) + list(kwargs.items()))
        return file.FileManager.clone(self, plainTextFileModel, **args)


class PlainTextFile(file.File):
    source_code = models.TextField(blank=True)
    objects = PlainTextFileManager()

    class Meta:
        app_label = 'app'


    def getContent(self):
        output = StringIO.StringIO()
        output.write(self.source_code)
        return output

    def getSize(self):
        plaintextfile = self.getContent()

        old_file_position = plaintextfile.tell()
        plaintextfile.seek(0, SEEK_END)
        plaintextfilesize = plaintextfile.tell()
        plaintextfile.seek(old_file_position, SEEK_SET)
        plaintextfile.close()

        return plaintextfilesize


@receiver(pre_save, sender=PlainTextFile)
def plainTextFilePreSave(instance, **kwargs):
    if not instance.mimeType:
        instance.mimeType = 'text/plain'
    instance.size = instance.getSize()
