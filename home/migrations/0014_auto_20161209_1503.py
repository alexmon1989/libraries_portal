# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-09 13:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_libraryrequestaccess_approved'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='libraryrequestaccess',
            options={'verbose_name': 'Заявка на получение доступа', 'verbose_name_plural': 'Заявки на получение доступа'},
        ),
        migrations.AlterField(
            model_name='libraryrequestaccess',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]