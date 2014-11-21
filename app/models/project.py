# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from app.models.folder import Folder


class Project(Folder):
    author = models.ForeignKey(User)