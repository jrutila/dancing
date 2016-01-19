# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0014_auto_20160118_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityparticipation',
            name='member',
            field=models.ForeignKey(related_name='activities', to='danceclub.Member'),
        ),
    ]
