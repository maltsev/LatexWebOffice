# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_squashed_0004_auto_20150228_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='lockexpires',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
