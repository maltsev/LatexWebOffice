# -*- coding: utf-8 -*-
from app.models.file import binaryfile


class Image(binaryfile.BinaryFile):
    objects = binaryfile.BinaryFileManager()