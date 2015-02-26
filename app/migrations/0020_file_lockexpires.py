# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_file_lasteditor'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='lockexpires',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
