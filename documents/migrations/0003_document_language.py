# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-07 08:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20161206_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='language',
            field=models.CharField(default=1, max_length=255, verbose_name='Язык'),
            preserve_default=False,
        ),
    ]
