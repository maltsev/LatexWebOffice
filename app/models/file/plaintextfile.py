# -*- coding: utf-8 -*-
from django.db import models
from app.models.file.file import File


class PlainTextFile(File):
    source_code = models.TextField(blank=True)