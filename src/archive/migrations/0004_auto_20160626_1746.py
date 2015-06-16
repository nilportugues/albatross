# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0003_archive_allow_consumption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archive',
            name='size',
            field=models.BigIntegerField(default=0, help_text='The size, in bytes, of the tweets field'),
        ),
        migrations.AlterField(
            model_name='archive',
            name='total',
            field=models.BigIntegerField(default=0),
        ),
    ]
