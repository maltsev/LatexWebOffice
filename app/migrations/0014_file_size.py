# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20141130_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='size',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
