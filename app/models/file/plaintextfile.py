# -*- coding: utf-8 -*-
"""

* Purpose :  Modell (app/models/file/)

* Creation Date : 26-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import io
from django.db import models
from app.models.file.file import File


class PlainTextFile(File):
    source_code = models.TextField(blank=True)

    def getContent(self):
        output = io.StringIO()
        output.write(self.source_code)
        return output