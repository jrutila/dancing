# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0027_danceevent_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='danceevent',
            name='deadline',
            field=models.DateTimeField(blank=True, null=True, help_text='Ilmoittautumaan pystyy ennen tätä hetkeä'),
        ),
    ]
