# -*- coding: utf-8 -*-
from django.db import models


class File(models.Model):
    name = models.CharField(max_length=255)
    source_code = models.TextField()

    def __str__(self):
        return self.name