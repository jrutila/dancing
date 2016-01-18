# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0013_danceevent_extra'),
    ]

    operations = [
        migrations.AlterField(
            model_name='danceevent',
            name='extra',
            field=models.TextField(help_text='Lisätietoja', blank=True),
        ),
    ]
