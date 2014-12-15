# -*- coding: utf-8 -*-
"""

* Purpose : Verzeichnis Modell (app/models/folder.py)

* Creation Date : 21-11-2014

* Last Modified : 4 Dec 2014 13:17:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
import os

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.image import Image
from app.models.file.pdf import PDF
from app.models.file.file import File
import app
from app.models.file.binaryfile import BinaryFile
from core import settings


class FolderManager(models.Manager):
    def copy(self, fromFolder, toFolder):
        toRootFolder = toFolder.getRoot()

        for fileOrFolder in fromFolder.getFilesAndFolders():
            if isinstance(fileOrFolder, File):
                file = fileOrFolder

                try:
                    existingFile = File.objects.get(name=file.name, folder=toFolder)
                    existingFile.delete()
                except ObjectDoesNotExist:
                    pass

                file.__class__.objects.clone(file, folder=toFolder)

            else:
                fromSubFolder = fileOrFolder
                toSubFolder = Folder.objects.get(pk=fromSubFolder.pk)  # Clone
                toSubFolder.pk = None
                toSubFolder.parent = toFolder
                toSubFolder.root = toRootFolder
                toSubFolder.save()

                self.copy(fromSubFolder, toSubFolder)


class Folder(models.Model):
    name = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", blank=True, null=True,
                               related_name='children')  # Darf leer sein nur bei RootFolder
    root = models.ForeignKey("self", blank=True, null=True,
                             related_name='rootFolder')  # Darf leer sein nur bei RootFolder
    objects = FolderManager()

    ##
    # Prüft ob das Verzeichnis ein Rootverzeichnis ist
    def isRoot(self):
        return not self.root or self.root is self

    ##
    # Gibt das Rooverzeichnis zurück
    # @return app.models.folder.Folder
    def getRoot(self):
        if self.isRoot():
            return self
        return self.root

    ##
    # Gibt das Projekt zurück
    # @return app.models.project.Project
    def getProject(self):
        projectTemplate = self.getRoot().projecttemplate
        try:
            return app.models.project.Project.objects.get(pk=projectTemplate.pk)
        except ObjectDoesNotExist:
            return projectTemplate


    ##
    # Gibt die MainTexDatei zurück
    # @return app.models.file.texfile.TexFile
    def getMainTex(self):
        rootFolder = self.getRoot()
        file = rootFolder.file_set.filter(name='main.tex').get()
        return TexFile.objects.get(pk=file.pk)

    ##
    # Abbildet das Vezeichnis auf der Festplatte und gibt
    # den temporären Verzeichnispfad zurück
    # @return String
    def getTempPath(self):
        if self.parent:
            folderPath = os.path.join(self.parent.getTempPath(), self.name)
        else:
            folderPath = os.path.join(settings.PROJECT_ROOT, "{}_{}".format(self.pk, self.name))

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        return folderPath

    ##
    # Bildet ein komplettes Verzeichnis auf der Festplatte ab
    # und gibt den temporären Vezeichnispfad zurück
    # @return String
    def dumpFolder(self):
        for fileOrFolder in self.getFilesAndFoldersRecursively():
            fileOrFolder.getTempPath()

        return self.getTempPath()

    ##
    # Gibt alle innere Dateien und Verzeichnise des Verzeichnises zurück
    # @return eine Liste mit app.models.file.File und app.models.folder.Folder
    def getFilesAndFolders(self):
        # Wir können alle Dateien mit File.objects.filter(..).all() bekommen.
        # Aber dann werden diese Dateien als app.models.file.File sein.
        # Deshalb bekommen wir jeden Dateityp einzeln.

        excludeFileIds = []

        texFiles = list(TexFile.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in texFiles]

        plainTextFiles = list(PlainTextFile.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in plainTextFiles]

        imageFiles = list(Image.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in imageFiles]

        pdfFiles = list(PDF.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in pdfFiles]

        binaryFiles = list(BinaryFile.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())
        excludeFileIds = excludeFileIds + [file.pk for file in binaryFiles]

        files = list(File.objects.filter(folder=self).exclude(pk__in=excludeFileIds).all())

        folders = list(self.children.all())

        return texFiles + plainTextFiles + imageFiles + pdfFiles + folders + binaryFiles + files

    ##
    # Gibt rekursiv alle innere Dateien und Verzeichnise des Verzeichnises zurück
    # @return eine Liste mit app.models.file.File und app.models.folder.Folder
    def getFilesAndFoldersRecursively(self):
        filesAndFolders = self.getFilesAndFolders()
        for fileOrFolder in filesAndFolders:
            if hasattr(fileOrFolder, 'getFilesAndFoldersRecursively') \
                    and callable(fileOrFolder.getFilesAndFoldersRecursively):
                folder = fileOrFolder
                filesAndFolders = filesAndFolders + folder.getFilesAndFoldersRecursively()

        return filesAndFolders


    def __str__(self):
        if self.isRoot():
            try:
                return "{}/".format(self.getProject())
            except ObjectDoesNotExist:
                return "{}/".format(self.name)
        else:
            return "{}{}/".format(self.parent, self.name)


@receiver(post_save, sender=Folder)
def folderPreSave(instance, **kwargs):
    if instance.isRoot():
        TexFile.objects.get_or_create(name='main.tex', folder=instance)
