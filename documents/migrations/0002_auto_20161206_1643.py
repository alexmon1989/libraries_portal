# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-06 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='anotherperson',
            options={'verbose_name': 'Другая персоны', 'verbose_name_plural': 'Другие персоны'},
        ),
        migrations.AlterModelOptions(
            name='document',
            options={'verbose_name': 'Документ', 'verbose_name_plural': 'Документы'},
        ),
        migrations.AlterModelOptions(
            name='documenttype',
            options={'verbose_name': 'Тип документа', 'verbose_name_plural': 'Типы документов'},
        ),
        migrations.AddField(
            model_name='document',
            name='catalog_number',
            field=models.CharField(default=1, max_length=255, verbose_name='Шифр хранения (№ в каталоге)'),
            preserve_default=False,
        ),
    ]
