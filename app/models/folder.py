# -*- coding: utf-8 -*-
"""

* Purpose :  Modell (app/models/file/)

* Creation Date : 21-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.image import Image
from app.models.file.pdf import PDF
from app.models.file.file import File
from core import settings


class Folder(models.Model):
    name = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True)
    # Darf leer sein nur bei RootFolder
    parent = models.ForeignKey(
        "self", blank=True, null=True, related_name='children')
    # Darf leer sein nur bei RootFolder
    root = models.ForeignKey(
        "self", blank=True, null=True, related_name='rootFolder')

    def isRoot(self):
        return not self.root or self.root is self

    def getRoot(self):
        if self.isRoot():
            return self
        return self.root

    def getProject(self):
        return self.getRoot().project_set.get()

    def getMainTex(self):
        rootFolder = self.getRoot()
        file = rootFolder.file_set.filter(name='main.tex').get()
        return TexFile.objects.get(pk=file.pk)

    def getTempPath(self):
        if self.parent:
            folderPath = os.path.join(self.parent.getTempPath(), self.name)
        else:
            folderPath = os.path.join(
                settings.BASE_DIR, 'media', 'projects', str(self.pk) + '_' + self.name)

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        return folderPath

    def dumpRootFolder(self):
        root = self.getRoot()
        for fileOrFolder in self.getFilesAndFoldersRecursively():
            fileOrFolder.getTempPath()

        return root.getTempPath()

    def getFilesAndFolders(self):
        excludeFileIds = []

        texFiles = list(
            TexFile.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in texFiles]

        plainTextFiles = list(
            PlainTextFile.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in plainTextFiles]

        imageFiles = list(
            Image.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in imageFiles]

        pdfFiles = list(
            PDF.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in pdfFiles]

        files = list(
            File.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())

        folders = list(self.children.all())

        return texFiles + plainTextFiles + imageFiles + pdfFiles + folders + files

    def getFilesAndFoldersRecursively(self):
        filesAndFolders = self.getFilesAndFolders()
        for fileOrFolder in filesAndFolders:
            if hasattr(fileOrFolder, 'getFilesAndFoldersRecursively') and callable(fileOrFolder.getFilesAndFoldersRecursively):
                folder = fileOrFolder
                filesAndFolders = filesAndFolders + \
                    folder.getFilesAndFoldersRecursively()

        return filesAndFolders

    def __str__(self):
        return self.name


@receiver(post_save, sender=Folder)
def folderPreSave(instance, **kwargs):
    if instance.isRoot():
        TexFile.objects.get_or_create(name='main.tex', folder=instance)
