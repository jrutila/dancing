# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0034_owncompetition_place_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='owncompetition',
            name='deadline',
            field=models.DateTimeField(help_text='Mihin asti saa ilmoittautua netin kautta', default=datetime.datetime(2016, 9, 16, 10, 21, 50, 21538, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
