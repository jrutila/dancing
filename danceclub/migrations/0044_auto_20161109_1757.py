# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0043_auto_20161023_2327'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitionparticipation',
            name='number',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='competitionparticipation',
            name='paid',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
