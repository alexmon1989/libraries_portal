# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-02 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20161202_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес'),
        ),
    ]
