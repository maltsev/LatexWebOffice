# -*- coding: utf-8 -*-
import io
from django.db import models
from app.models.file.file import File


class PlainTextFile(File):
    source_code = models.TextField(blank=True)

    def getContent(self):
        output = io.StringIO()
        output.write(self.source_code)
        return output