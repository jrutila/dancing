# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0024_auto_20160318_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='danceeventparticipation',
            name='dancer',
        ),
        migrations.AddField(
            model_name='danceeventparticipation',
            name='member',
            field=models.ForeignKey(default=1, to='danceclub.Member'),
            preserve_default=False,
        ),
    ]
