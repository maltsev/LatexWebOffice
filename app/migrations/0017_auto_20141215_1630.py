# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='size',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
