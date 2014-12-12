# -*- coding: utf-8 -*-
"""

* Purpose : TeX-datei Modell (app/models/file/texfile.py)

* Creation Date : 20-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from app.models.file.plaintextfile import PlainTextFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class TexFile(PlainTextFile):

    def getSize(self):
        texfile = self.getContent()

        old_file_position = texfile.tell()
        texfile.seek(0, os.SEEK_END)
        texfilesize = texfile.tell()
        texfile.seek(old_file_position, os.SEEK_SET)
        texfile.close()

        return texfilesize

@receiver(pre_save, sender=TexFile)
def texFilePreSave(instance, **kwargs):
    instance.mimeType = 'text/x-tex'
    instance.size = instance.getSize()