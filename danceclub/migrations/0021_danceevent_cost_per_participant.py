# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0020_danceeventparticipation_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='danceevent',
            name='cost_per_participant',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
