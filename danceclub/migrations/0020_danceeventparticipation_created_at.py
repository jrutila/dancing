# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0019_danceevent_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='danceeventparticipation',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
