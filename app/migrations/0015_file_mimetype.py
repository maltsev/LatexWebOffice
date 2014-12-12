# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_file_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='mimeType',
            field=models.CharField(default='application/octet-stream', max_length=255),
            preserve_default=True,
        ),
    ]
