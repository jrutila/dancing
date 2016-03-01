# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0017_member_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='couple',
            name='level',
        ),
        migrations.RemoveField(
            model_name='couple',
            name='points',
        ),
        migrations.AddField(
            model_name='couple',
            name='level_latin',
            field=models.CharField(blank=True, null=True, choices=[('F', 'F'), ('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('A', 'A')], max_length=1),
        ),
        migrations.AddField(
            model_name='couple',
            name='level_standard',
            field=models.CharField(blank=True, null=True, choices=[('F', 'F'), ('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('A', 'A')], max_length=1),
        ),
        migrations.AddField(
            model_name='couple',
            name='points_latin',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='couple',
            name='points_standard',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
