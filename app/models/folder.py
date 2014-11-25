# -*- coding: utf-8 -*-
from django.db import models

class Folder(models.Model):
    name = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", blank=True, null=True, related_name='parentFolder') # Darf leer sein nur bei RootFolder
    root = models.ForeignKey("self", blank=True, null=True, related_name='rootFolder') # Darf leer sein nur bei RootFolder

    def is_root(self):
        return self.parent == self.root

    def __str__(self):
        return self.name

    def getRootFolder(self):
        if self.parentFolder==None:
            return self
        else:
            return self.parentFolder.getRootFolder()
