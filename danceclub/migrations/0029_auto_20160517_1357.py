# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0028_auto_20160504_0730'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='danceeventparticipation',
            options={'permissions': (('view_danceeventparticipation', 'Can see all dance event participations'),)},
        ),
    ]
