# -*- coding: utf-8 -*-
from django.db import models
from app.models.file import file


class TexFile(file.File):
    title = models.CharField(max_length=255, blank=True)
    source_code = models.TextField(blank=True)

    class Meta:
        abstract = True