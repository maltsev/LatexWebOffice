# -*- coding: utf-8 -*-
"""

* Purpose : TeX-datei Modell (app/models/file/texfile.py)

* Creation Date : 20-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from app.models.file import plaintextfile


class TexFile(plaintextfile.PlainTextFile):
    objects = plaintextfile.PlainTextFileManager()