# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20141130_2228'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='project',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='project',
            name='author',
        ),
        migrations.RemoveField(
            model_name='project',
            name='rootFolder',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]
