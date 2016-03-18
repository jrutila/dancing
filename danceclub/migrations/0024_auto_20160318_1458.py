# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0023_member_young'),
    ]

    operations = [
        migrations.AlterField(
            model_name='danceeventparticipation',
            name='event',
            field=models.ForeignKey(to='danceclub.DanceEvent', related_name='participations'),
        ),
    ]
