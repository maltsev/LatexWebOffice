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


class PlainTextFile(File):
    source_code = models.TextField(blank=True)

    def getContent(self):
        output = io.StringIO()
        output.write(self.source_code)
        return output

@receiver(pre_save, sender=PlainTextFile)
def plainTextFilePreSave(instance, **kwargs):
    instance.mimeType = 'text/plain'