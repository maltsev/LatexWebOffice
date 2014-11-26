# -*- coding: utf-8 -*-
from django.db import models
from app.models.file.file import File


class BinaryFile(File):
    filepath = models.CharField(max_length=255)