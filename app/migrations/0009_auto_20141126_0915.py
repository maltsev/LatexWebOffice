# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20141125_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='rootFolder',
            field=models.OneToOneField(to='app.Folder'),
        ),
    ]
