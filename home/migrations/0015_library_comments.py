# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-12 13:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
        ('home', '0014_auto_20161209_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='library',
            name='comments',
            field=models.ManyToManyField(blank=True, to='comments.Comment', verbose_name='Комментарии'),
        ),
    ]
