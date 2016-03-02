# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0021_danceevent_cost_per_participant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='danceeventparticipation',
            name='cancelled',
        ),
        migrations.AlterField(
            model_name='danceevent',
            name='cost_per_participant',
            field=models.BooleanField(help_text='Valitse tämä, jos maksu on per osallistuja'),
        ),
    ]
