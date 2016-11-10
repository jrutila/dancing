# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0044_auto_20161109_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionparticipation',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='competitionparticipation',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
