# -*- coding: utf-8 -*-
"""

* Purpose :  Django Adminpanel

* Creation Date : 22-11-2014

* Last Modified : 1 Dec 2014 22:13:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
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
    list_display = ('name','folder')

