# -*- coding: utf-8 -*-
"""

* Purpose : Binärdatei Modell (app/models/file/binaryfile.py)

* Creation Date : 26-11-2014

* Last Modified : 4 Dec 2014 13:17:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import os, hashlib
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from core import settings
from app.models.file import file


class BinaryFileManager(file.FileManager):
    def clone(self, binaryFileModel, **kwargs):
        defaultArgs = {
            'name': binaryFileModel.name,
            'folder': binaryFileModel.folder,
            'file': open(binaryFileModel.filepath, 'rb')
        }
        args = dict(list(defaultArgs.items()) + list(kwargs.items()))
        return binaryFileModel.__class__.objects.createFromFile(**args)


    ##
    # BinaryFile Erzeugung von request.FILES
    # https://docs.djangoproject.com/en/dev/topics/http/file-uploads/
    def createFromRequestFile(self, **kwargs):
        isFilepath = 'filepath' in kwargs and bool(kwargs['filepath'])
        requestFile = 'requestFile' in kwargs and kwargs['requestFile']
        if requestFile and not isFilepath:
            content = b''
            for chunk in requestFile.chunks():
                content = content + chunk

            kwargs['filepath'], kwargs['size'] = self.__createBinaryFile(content)
            del kwargs['requestFile']

        return self.create(**kwargs)

    ##
    # BinaryFile Erzeugung von Python File
    def createFromFile(self, **kwargs):
        isFilepath = 'filepath' in kwargs and bool(kwargs['filepath'])
        file = 'file' in kwargs and kwargs['file']
        if file and not isFilepath:
            kwargs['filepath'], kwargs['size'] = self.__createBinaryFile(file.read())
            del kwargs['file']

        return self.create(**kwargs)


    def __createBinaryFile(self, content):
        filename = hashlib.md5(content).hexdigest()
        filepath = os.path.join(settings.FILE_ROOT, filename)
        if not os.path.exists(filepath):
            fileDirPath = os.path.dirname(filepath)
            if not os.path.exists(fileDirPath):
                os.makedirs(fileDirPath)

            newFile = open(filepath, 'wb')
            newFile.write(content)
            newFile.close()

        return filepath, os.path.getsize(filepath)




class BinaryFile(file.File):
    filepath = models.CharField(max_length=255)
    objects = BinaryFileManager()

    def getContent(self):
        return open(str(self.filepath), 'rb')


@receiver(post_delete, sender=BinaryFile)
def binaryFilePostDelete(instance, **kwargs):
    if os.path.isfile(instance.filepath):
        os.remove(instance.filepath)