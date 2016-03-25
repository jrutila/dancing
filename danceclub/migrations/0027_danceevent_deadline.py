# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0026_danceevent_public_since'),
    ]

    operations = [
        migrations.AddField(
            model_name='danceevent',
            name='deadline',
            field=models.DateTimeField(help_text='Ilmoittautua pystyy ennen tätä hetkeä', default=datetime.datetime(2016, 3, 24, 15, 9, 20, 523178, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
