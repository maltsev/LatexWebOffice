# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_remove_document_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='author',
        ),
        migrations.RemoveField(
            model_name='document',
            name='project',
        ),
        migrations.DeleteModel(
            name='Document',
        ),
        migrations.RemoveField(
            model_name='project',
            name='author',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]
