# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-07-29 05:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0002_auto_20170729_0513'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='journal',
            table='Journal',
        ),
    ]