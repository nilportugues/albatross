# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(max_length=64, unique=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='Staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active', help_text='Designates whether this user can log into the primary site.')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('durations_available', django.contrib.postgres.fields.ArrayField(size=None, default=[30, 60, 180, 360], base_field=models.PositiveIntegerField(null=True, blank=True, choices=[(30, '30m'), (60, '1h'), (180, '3h'), (360, '6h'), (720, '12h'), (1440, '24h'), (2880, '48h'), (4320, '72h'), (10080, '7d'), (20160, '14d'), (525600, '30d'), (0, '∞')]), choices=[(30, '30m'), (60, '1h'), (180, '3h'), (360, '6h'), (720, '12h'), (1440, '24h'), (2880, '48h'), (4320, '72h'), (10080, '7d'), (20160, '14d'), (525600, '30d'), (0, '∞')])),
                ('status', models.PositiveIntegerField(default=1, verbose_name='Twitter Status', help_text='A user is marked as "disabled" when the collector receives a 401 from Twitter', choices=[(1, 'Active'), (2, 'Disabled')])),
                ('groups', models.ManyToManyField(related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', to='auth.Group', related_name='user_set', blank=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', help_text='Specific permissions for this user.', verbose_name='user permissions', to='auth.Permission', related_name='user_set', blank=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
