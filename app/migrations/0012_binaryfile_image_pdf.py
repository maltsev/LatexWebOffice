# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_plaintextfile_texfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='BinaryFile',
            fields=[
                ('file_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='app.File', serialize=False)),
                ('filepath', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=('app.file',),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('binaryfile_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='app.BinaryFile', serialize=False)),
            ],
            options={
            },
            bases=('app.binaryfile',),
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('binaryfile_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='app.BinaryFile', serialize=False)),
            ],
            options={
            },
            bases=('app.binaryfile',),
        ),
    ]
