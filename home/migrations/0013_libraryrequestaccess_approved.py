# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-09 12:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_libraryrequestaccess'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryrequestaccess',
            name='approved',
            field=models.BooleanField(default=False, verbose_name='Утверждено'),
        ),
    ]