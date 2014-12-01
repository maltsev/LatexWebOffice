# -*- coding: utf-8 -*-
"""

* Purpose :  Modell (app/models/file/)

* Creation Date : 26-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from app.models.file import binaryfile


class Image(binaryfile.BinaryFile):
    objects = binaryfile.BinaryFileManager()
