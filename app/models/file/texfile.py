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
    pass

@receiver(pre_save, sender=TexFile)
def texFilePreSave(instance, **kwargs):
    instance.mimeType = 'text/x-tex'
    instance.size = instance.getSize()