# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0007_auto_20141124_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(
                    serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('lastModifiedTime', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(
                    serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(
                    to='app.Folder', related_name='parentFolder', blank=True, null=True)),
                ('root', models.ForeignKey(
                    to='app.Folder', related_name='rootFolder', blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(
                    serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('rootFolder', models.ForeignKey(to='app.Folder')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TexFile',
            fields=[
                ('file_ptr', models.OneToOneField(serialize=False, auto_created=True,
                                                  parent_link=True, primary_key=True, to='app.File')),
                ('source_code', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=set([('name', 'author')]),
        ),
        migrations.AddField(
            model_name='file',
            name='folder',
            field=models.ForeignKey(to='app.Folder'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('name', 'folder')]),
        ),
    ]
