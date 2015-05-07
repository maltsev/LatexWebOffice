# -*- coding: utf-8 -*-
"""

* Purpose : PDF-Datei Modell (app/models/file/pdf.py)

* Creation Date : 26-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from app.models.file import binaryfile
from django.db.models.signals import pre_save
from django.dispatch import receiver


class PDF(binaryfile.BinaryFile):
    objects = binaryfile.BinaryFileManager()

    class Meta:
        app_label = 'app'


@receiver(pre_save, sender=PDF)
def pdfPreSave(instance, **kwargs):
    instance.mimeType = 'application/pdf'