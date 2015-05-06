# -*- coding: utf-8 -*-
"""

* Purpose :  Django Adminpanel

* Creation Date : 22-11-2014

* Last Modified : Do 26 Feb 2015 13:30:25 CET

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



class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'relativePath', 'createTime', 'parent', 'root')
    list_filter = ('parent', 'root')
    form = FolderForm

    def relativePath(self, obj):
        return str(obj)
    relativePath.short_description = 'Path'


admin.site.register(models.folder.Folder, FolderAdmin)



class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'isConfirmed')

admin.site.register(models.collaboration.Collaboration, CollaborationAdmin)



class ProjectTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'createTime')
    list_filter = ('author',)
    exclude = ('rootFolder',)

admin.site.register(models.projecttemplate.ProjectTemplate, ProjectTemplateAdmin)



class ProjectAdmin(ProjectTemplateAdmin):
    pass

admin.site.register(models.project.Project, ProjectAdmin)



class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'relativePath', 'createTime', 'lastModifiedTime', 'lock')
    list_filter = ('folder',)

    def relativePath(self, obj):
        return str(obj)
    relativePath.short_description = 'Path'

    def lock(self, obj):
        return obj.isLocked()
    lock.boolean = True



class TexFileAdmin(FileAdmin):
    pass

admin.site.register(models.texfile.TexFile, TexFileAdmin)



class ImageAdmin(FileAdmin):
    pass

admin.site.register(models.image.Image, ImageAdmin)



class BinaryFileAdmin(FileAdmin):
    pass

admin.site.register(models.binaryfile.BinaryFile, BinaryFileAdmin)



class PlainTextFileAdmin(FileAdmin):
    pass

admin.site.register(models.plaintextfile.PlainTextFile, PlainTextFileAdmin)




