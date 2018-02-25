# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('started', models.DateTimeField(auto_created=True)),
                ('query', models.CharField(max_length=32)),
                ('stopped', models.DateTimeField(blank=True, null=True, help_text='Defaults to start + 24hours')),
                ('is_running', models.BooleanField(default=False)),
                ('allow_search', models.BooleanField(default=False)),
                ('last_distilled', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(1, 'Active'), (2, 'Disabled')], default=1)),
                ('cloud', models.TextField(blank=True)),
                ('statistics', models.TextField(blank=True)),
                ('images', models.TextField(blank=True)),
                ('cloud_generated', models.DateTimeField(blank=True, null=True)),
                ('map_generated', models.DateTimeField(blank=True, null=True)),
                ('search_generated', models.DateTimeField(blank=True, null=True)),
                ('statistics_generated', models.DateTimeField(blank=True, null=True)),
                ('images_generated', models.DateTimeField(blank=True, null=True)),
                ('colour_overrides', models.TextField(blank=True, help_text='A JSON field used to override the colours used by c3 in generating pie charts.')),
                ('total', models.PositiveIntegerField(default=0)),
                ('size', models.PositiveIntegerField(help_text='The size, in bytes, of the tweets field', default=0)),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='archives', on_delete=models.PROTECT)),
            ],
            options={
                'ordering': ('-started',),
            },
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('created', models.DateTimeField(db_index=True)),
                ('mentions', django.contrib.postgres.fields.ArrayField(blank=True, null=True, base_field=models.CharField(max_length=64), size=None)),
                ('hashtags', django.contrib.postgres.fields.ArrayField(blank=True, null=True, base_field=models.CharField(max_length=280), size=None)),
                ('text', models.CharField(max_length=256, db_index=True)),
                ('archive', models.ForeignKey(related_name='tweets', to='archive.Archive', on_delete=models.CASCADE)),
            ],
        ),
    ]
