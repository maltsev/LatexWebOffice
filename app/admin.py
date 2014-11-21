# -*- coding: utf-8 -*-
from django.contrib import admin
from app import models


@admin.register(models.project.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'createTime')


@admin.register(models.document.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'project', 'createTime', 'lastModifiedTime')
    list_filter = ('project',)