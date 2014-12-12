# -*- coding: utf-8 -*-
"""

* Purpose : Textdatei Modell (app/models/file/plaintextfile.py)

* Creation Date : 26-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import io
from django.db import models
from app.models.file.file import File
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os


class PlainTextFile(File):
    source_code = models.TextField(blank=True)

    def getContent(self):
        output = io.StringIO()
        output.write(self.source_code)
        return output

    def getSize(self):
        plaintextfile = self.getContent()

        old_file_position = plaintextfile.tell()
        plaintextfile.seek(0, os.SEEK_END)
        plaintextfilesize = plaintextfile.tell()
        plaintextfile.seek(old_file_position, os.SEEK_SET)
        plaintextfile.close()

        return plaintextfilesize

@receiver(pre_save, sender=PlainTextFile)
def plainTextFilePreSave(instance, **kwargs):
    instance.mimeType = 'text/plain'
    instance.size = instance.getSize()