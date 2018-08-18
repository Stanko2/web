# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-15 16:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0011_auto_20180611_1626'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskpeople',
            options={'verbose_name': 'Pridelený človek', 'verbose_name_plural': 'Pridelení ľudia'},
        ),
        migrations.AddField(
            model_name='task',
            name='email_on_code_submit',
            field=models.BooleanField(default=False, verbose_name='Send notification to reviewers about new code submit'),
        ),
        migrations.AddField(
            model_name='task',
            name='email_on_desc_submit',
            field=models.BooleanField(default=False, verbose_name='Send notification to reviewers about new description submit'),
        ),
        migrations.AlterField(
            model_name='taskpeople',
            name='role',
            field=models.IntegerField(choices=[(0, 'opravovateľ'), (1, 'solution writer'), (2, 'recenzovač')], verbose_name='funkcia'),
        ),
        migrations.AlterField(
            model_name='taskpeople',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='vedúci'),
        ),
    ]