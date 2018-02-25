# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('time', models.DateTimeField()),
                ('label', models.CharField(max_length=64)),
                ('archive', models.ForeignKey(to='archive.Archive', related_name='events', on_delete=models.CASCADE)),
            ],
        ),
    ]
