# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0002_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='allow_consumption',
            field=models.BooleanField(default=True, help_text='Should incoming tweets actually be consumed or just left in the queue?'),
        ),
    ]
