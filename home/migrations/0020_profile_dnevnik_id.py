# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-22 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_auto_20161220_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='dnevnik_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='id в Дневник.ру'),
        ),
    ]
