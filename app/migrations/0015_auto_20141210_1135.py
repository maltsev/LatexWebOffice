# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0014_auto_20141210_1037'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTemplate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('createTime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('projecttemplate_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='app.ProjectTemplate', auto_created=True, serialize=False)),
            ],
            options={
            },
            bases=('app.projecttemplate',),
        ),
        migrations.AddField(
            model_name='projecttemplate',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projecttemplate',
            name='rootFolder',
            field=models.OneToOneField(to='app.Folder'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='projecttemplate',
            unique_together=set([('name', 'author')]),
        ),
    ]
