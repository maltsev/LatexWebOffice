# -*- coding: utf-8 -*-
from django.contrib import admin
from app import models


@admin.register(models.folder.Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createTime', 'parent', 'root')
    list_filter = ('parent', 'root')


@admin.register(models.project.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'createTime', 'rootFolder')
    list_filter = ('author',)


@admin.register(models.texfile.TexFile)
class TexFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'folder', 'createTime', 'lastModifiedTime')
    list_filter = ('folder',)


@admin.register(models.file.File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'folder')
