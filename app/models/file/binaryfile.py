# -*- coding: utf-8 -*-
import os
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from app.models.file.file import File


class BinaryFile(File):
    filepath = models.CharField(max_length=255)

    def getContent(self):
        return open(str(self.filepath), 'r')


@receiver(post_delete, sender=BinaryFile)
def binaryFilePostDelete(instance, **kwargs):
    if os.path.isfile(instance.filepath):
        os.remove(instance.filepath)