# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LatexWebUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('first_name', models.CharField(max_length=30, blank=True)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('isConfirmed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('lastModifiedTime', models.DateTimeField(auto_now=True)),
                ('mimeType', models.CharField(default='application/octet-stream', max_length=255)),
                ('size', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BinaryFile',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.File', serialize=False, auto_created=True)),
                ('filepath', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, related_name='children', to='app.Folder', null=True)),
                ('root', models.ForeignKey(blank=True, related_name='rootFolder', to='app.Folder', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('binaryfile_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.BinaryFile', serialize=False, auto_created=True)),
            ],
            options={
            },
            bases=('app.binaryfile',),
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('binaryfile_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.BinaryFile', serialize=False, auto_created=True)),
            ],
            options={
            },
            bases=('app.binaryfile',),
        ),
        migrations.CreateModel(
            name='PlainTextFile',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.File', serialize=False, auto_created=True)),
                ('source_code', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.CreateModel(
            name='ProjectTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('projecttemplate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.ProjectTemplate', serialize=False, auto_created=True)),
                ('collaborators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='app.Collaboration')),
            ],
            options={
            },
            bases=('app.projecttemplate',),
        ),
        migrations.CreateModel(
            name='TexFile',
            fields=[
                ('plaintextfile_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.PlainTextFile', serialize=False, auto_created=True)),
            ],
            options={
            },
            bases=('app.plaintextfile',),
        ),
        migrations.AddField(
            model_name='projecttemplate',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projecttemplate',
            name='rootFolder',
            field=models.OneToOneField(to='app.Folder'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='projecttemplate',
            unique_together=set([('name', 'author')]),
        ),
        migrations.AddField(
            model_name='file',
            name='folder',
            field=models.ForeignKey(to='app.Folder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='file',
            name='lasteditor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('name', 'folder')]),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='project',
            field=models.ForeignKey(to='app.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collaboration',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
