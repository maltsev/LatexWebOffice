# -*- coding: utf-8 -*-
from app.models.file import binaryfile


class PDF(binaryfile.BinaryFile):
    objects = binaryfile.BinaryFileManager()
