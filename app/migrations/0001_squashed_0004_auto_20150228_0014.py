# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('app', '0001_initial'), ('app', '0002_auto_20150226_1521'), ('app', '0003_latexwebuser_username'), ('app', '0004_auto_20150228_0014')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LatexWebUser',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('email', models.EmailField(unique=True, verbose_name='email address', max_length=255)),
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
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('isConfirmed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
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
                ('file_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='app.File')),
                ('filepath', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(to='app.Folder', related_name='children', blank=True, null=True)),
                ('root', models.ForeignKey(to='app.Folder', related_name='rootFolder', blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('binaryfile_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='app.BinaryFile')),
            ],
            options={
            },
            bases=('app.binaryfile',),
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('binaryfile_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='app.BinaryFile')),
            ],
            options={
            },
            bases=('app.binaryfile',),
        ),
        migrations.CreateModel(
            name='PlainTextFile',
            fields=[
                ('file_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='app.File')),
                ('source_code', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.CreateModel(
            name='ProjectTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
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
                ('projecttemplate_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='app.ProjectTemplate')),
                ('collaborators', models.ManyToManyField(through='app.Collaboration', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('app.projecttemplate',),
        ),
        migrations.CreateModel(
            name='TexFile',
            fields=[
                ('plaintextfile_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='app.PlainTextFile')),
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
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
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
        migrations.AddField(
            model_name='latexwebuser',
            name='passwordlostdate',
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0)),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='latexwebuser',
            name='passwordlostkey',
            field=models.CharField(blank=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='latexwebuser',
            name='username',
            field=models.CharField(blank=True, max_length=30),
            preserve_default=True,
        ),
    ]
