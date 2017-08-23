# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-23 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_mode', '0003_auto_20170822_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_text', models.TextField(blank=True, null=True)),
                ('category_id', models.BigIntegerField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('search_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('search_timestamp',),
                'verbose_name': 'Search result',
                'verbose_name_plural': 'Search results',
            },
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('created_date',), 'verbose_name': 'News', 'verbose_name_plural': 'News'},
        ),
        migrations.AlterModelOptions(
            name='request',
            options={'ordering': ('search_timestamp',), 'verbose_name': 'Search request', 'verbose_name_plural': 'Search requests'},
        ),
    ]
