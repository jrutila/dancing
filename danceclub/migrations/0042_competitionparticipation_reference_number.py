# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0041_auto_20161020_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitionparticipation',
            name='reference_number',
            field=models.ForeignKey(blank=True, to='danceclub.ReferenceNumber', null=True),
        ),
    ]
