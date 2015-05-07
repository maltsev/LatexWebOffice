# -*- coding: utf-8 -*-
"""

* Purpose : Kooperation Modell (app/models/collaboration.py)

* Creation Date : 12-02-2015

* Last Modified : Do 26 Feb 2015 13:32:36 CET

* Author :  maltsev

* Sprintnumber : 5

* Backlog entry :

"""
from django.db import models
from django.contrib.auth.models import User


class Collaboration(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey("Project")
    isConfirmed = models.BooleanField(default=False)

    class Meta:
        app_label = 'app'