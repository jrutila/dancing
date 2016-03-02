# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0018_auto_20160301_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='danceevent',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
            preserve_default=False,
        ),
    ]
