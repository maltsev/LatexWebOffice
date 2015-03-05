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

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from app.models.latexuserprofile import LatexWebUser as MyUser



class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email', 'first_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'first_name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()



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
    list_display = ('id', 'relativePath', 'createTime', 'lastModifiedTime', 'lock')
    list_filter = ('folder',)

    def relativePath(self, obj):
        return str(obj)
    relativePath.short_description = 'Path'

    def lock(self, obj):
        return obj.isLocked()
    lock.boolean = True


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




