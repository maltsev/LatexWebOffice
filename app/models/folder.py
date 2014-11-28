# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models.file.texfile import TexFile

class Folder(models.Model):
    name = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", blank=True, null=True, related_name='parentFolder') # Darf leer sein nur bei RootFolder
    root = models.ForeignKey("self", blank=True, null=True, related_name='rootFolder') # Darf leer sein nur bei RootFolder


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

    def __str__(self):
        return self.name



@receiver(post_save, sender=Folder)
def folderPreSave(instance, **kwargs):
    if instance.isRoot():
        TexFile.objects.get_or_create(name='main.tex', folder=instance)
