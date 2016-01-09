# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homeslide',
            name='text',
        ),
        migrations.RemoveField(
            model_name='homeslide',
            name='title',
        ),
        migrations.AddField(
            model_name='homeslide',
            name='slide_text',
            field=models.CharField(max_length=300, default='Moi'),
        ),
        migrations.AddField(
            model_name='homeslide',
            name='slide_title',
            field=models.CharField(max_length=50, default='Moi'),
        ),
    ]
