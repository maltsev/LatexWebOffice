# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20141126_1040'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlainTextFile',
            fields=[
                ('file_ptr', models.OneToOneField(serialize=False, parent_link=True, primary_key=True, to='app.File', auto_created=True)),
                ('source_code', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.CreateModel(
            name='TexFile',
            fields=[
                ('plaintextfile_ptr', models.OneToOneField(serialize=False, parent_link=True, primary_key=True, to='app.PlainTextFile', auto_created=True)),
            ],
            options={
            },
            bases=('app.plaintextfile',),
        ),
    ]
