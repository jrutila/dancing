# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0025_auto_20160318_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='danceevent',
            name='public_since',
            field=models.DateTimeField(help_text='Mistä hetkestä eteenpäin vapaasti varattavissa', null=True, blank=True),
        ),
    ]
