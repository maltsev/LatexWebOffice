# -*- coding: utf-8 -*-
import os
import tempfile
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from app.models.file.file import File


class BinaryFileManager(models.Manager):

    def createFromRequestFile(self, **kwargs):
        isFilepath = 'filepath' in kwargs and bool(kwargs['filepath'])
        requestFile = 'requestFile' in kwargs and kwargs['requestFile']
        if requestFile and not isFilepath:
            _, filepath = tempfile.mkstemp()
            newFile = open(filepath, 'wb')
            for chunk in requestFile.chunks():
                newFile.write(chunk)

            newFile.close()

            kwargs['filepath'] = filepath
            del kwargs['requestFile']

        return self.create(**kwargs)

    def createFromFile(self, **kwargs):
        isFilepath = 'filepath' in kwargs and bool(kwargs['filepath'])
        file = 'file' in kwargs and kwargs['file']
        if file and not isFilepath:
            _, filepath = tempfile.mkstemp()
            newFile = open(filepath, 'wb')
            file.seek(0)
            newFile.write(file.read())
            newFile.close()

            kwargs['filepath'] = filepath
            del kwargs['file']

        return self.create(**kwargs)


class BinaryFile(File):
    filepath = models.CharField(max_length=255)
    objects = BinaryFileManager()

    def getContent(self):
        return open(str(self.filepath), 'rb')


@receiver(post_delete, sender=BinaryFile)
def binaryFilePostDelete(instance, **kwargs):
    if os.path.isfile(instance.filepath):
        os.remove(instance.filepath)
