# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    title = models.CharField(max_length=255)
    createTime = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)

    def __str__(self):
        return self.title