# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-08 11:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_document_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Статус документа',
                'verbose_name_plural': 'Статусы документов',
            },
        ),
        migrations.AddField(
            model_name='document',
            name='document_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='documents.DocumentType', verbose_name='Статус документа'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.DocumentStatus', verbose_name='Тип документа'),
        ),
    ]
