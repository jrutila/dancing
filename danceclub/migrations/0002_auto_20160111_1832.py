# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dancer',
            name='level',
        ),
        migrations.RemoveField(
            model_name='dancer',
            name='points',
        ),
        migrations.AddField(
            model_name='couple',
            name='level',
            field=models.CharField(default=0, max_length=1, choices=[('F', 'F'), ('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('A', 'A')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='couple',
            name='points',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
