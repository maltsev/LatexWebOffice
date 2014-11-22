# -*- coding: utf-8 -*-
from django.db import models

class Folder(models.Model):
    name = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True)
    parentFolder = models.ForeignKey("self", null=True, blank=True)

    def __str__(self):
        return self.name

    def getRootFolder(self):
        if self.parentFolder==None:
            return self
        else:
            return self.parentFolder.getRootFolder()
