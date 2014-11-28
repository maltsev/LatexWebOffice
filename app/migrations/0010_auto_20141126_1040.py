# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20141126_0915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='texfile',
            name='file_ptr',
        ),
        migrations.DeleteModel(
            name='TexFile',
        ),
        migrations.AlterField(
            model_name='project',
            name='rootFolder',
            field=models.ForeignKey(to='app.Folder'),
        ),
    ]
