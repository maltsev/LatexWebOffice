# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0005_auto_20141121_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
                ('lastModifiedTime', models.DateTimeField(auto_now=True)),
                ('source_code', models.TextField(blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
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
                ('folder_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='app.Folder', parent_link=True, serialize=False)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('app.folder',),
        ),
        migrations.AddField(
            model_name='folder',
            name='parentFolder',
            field=models.ForeignKey(to='app.Folder', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='folder',
            field=models.ForeignKey(to='app.Folder'),
            preserve_default=True,
        ),
    ]
