# -*- coding: utf-8 -*-
"""

* Purpose :  Django Adminpanel

* Creation Date : 22-11-2014

* Last Modified : Mon 15 Dec 2014 04:30:18 PM CET

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
    list_display = ('id', 'relativePath', 'createTime', 'parent', 'root')
    list_filter = ('parent', 'root')
    form = FolderForm

    def relativePath(self, obj):
        return str(obj)
    relativePath.short_description = 'Path'


@admin.register(models.collaboration.Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'isConfirmed')


@admin.register(models.projecttemplate.ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'createTime')
    list_filter = ('author',)
    exclude = ('rootFolder',)


@admin.register(models.project.Project)
class ProjectAdmin(ProjectTemplateAdmin):
    pass


class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'relativePath', 'createTime', 'lastModifiedTime')
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
