# -*- coding: utf-8 -*-
"""

* Purpose :  Django Adminpanel

* Creation Date : 22-11-2014

* Last Modified : 2 Dec 2014 21:31:00 CET

* Author :  maltsev

* Sprintnumber : 2

* Backlog entry :

"""
from django import forms
from django.contrib import admin
from app import models


class FolderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)

        self.fields['parent'].required = True
        self.fields['root'].required = True

@admin.register(models.folder.Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('relativePath', 'createTime', 'parent', 'root')
    list_filter = ('parent', 'root')
    form = FolderForm

    def relativePath(self, obj):
        return str(obj)
    relativePath.short_description = 'Path'


@admin.register(models.project.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'createTime')
    list_filter = ('author',)
    exclude = ('rootFolder',)


class FileAdmin(admin.ModelAdmin):
    list_display = ('relativePath', 'createTime', 'lastModifiedTime')
    list_filter = ('folder',)

    def relativePath(self, obj):
        return str(obj)
    relativePath.short_description = 'Path'


@admin.register(models.texfile.TexFile)
class TexFileAdmin(FileAdmin):
    pass


@admin.register(models.image.Image)
class ImageAdmin(FileAdmin):
    pass


@admin.register(models.binaryfile.BinaryFile)
class BinaryFileAdmin(FileAdmin):
    pass

@admin.register(models.plaintextfile.PlainTextFile)
class PlainTextFileAdmin(FileAdmin):
    pass