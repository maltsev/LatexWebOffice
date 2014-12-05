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


class PDF(binaryfile.BinaryFile):
    objects = binaryfile.BinaryFileManager()