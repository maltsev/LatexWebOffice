# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
from app.models.folder import Folder


class Project(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    createTime = models.DateTimeField(auto_now_add=True)
    rootFolder = models.ForeignKey(Folder)

    class Meta:
        unique_together = ('name', 'author')

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Project)
def projectPostDelete(instance, **kwargs):
    instance.rootFolder.delete()
