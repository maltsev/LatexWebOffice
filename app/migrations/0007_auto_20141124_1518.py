# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20141121_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='author',
        ),
        migrations.RemoveField(
            model_name='document',
            name='folder',
        ),
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.RemoveField(
            model_name='folder',
            name='parentFolder',
        ),
        migrations.RemoveField(
            model_name='project',
            name='author',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
        migrations.DeleteModel(
            name='Folder',
        ),
    ]
