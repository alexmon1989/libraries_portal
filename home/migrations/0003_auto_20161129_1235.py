# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-29 10:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0002_auto_20161129_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name_plural': 'Город',
                'verbose_name': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('enabled', models.BooleanField(default=False, verbose_name='Включено')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.City', verbose_name='Город')),
                ('library_kind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.LibraryKind', verbose_name='Вид библиотеки')),
                ('library_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.LibraryType', verbose_name='Тип библиотеки')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Учётная запись пользователя')),
            ],
            options={
                'verbose_name_plural': 'Библиотека',
                'verbose_name': 'Библиотеки',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
            ],
            options={
                'verbose_name_plural': 'Регион',
                'verbose_name': 'Регионы',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Region', verbose_name='Регион'),
        ),
    ]
