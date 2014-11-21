# -*- coding: utf-8 -*-
from django.contrib import admin
from app import models


@admin.register(models.folder.Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'createTime', 'parentFolder')


@admin.register(models.project.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'createTime', 'author')


@admin.register(models.document.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'folder', 'createTime', 'lastModifiedTime')
    list_filter = ('folder',)


