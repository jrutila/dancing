# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0035_owncompetition_deadline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='owncompetition',
            name='tickets',
        ),
    ]
