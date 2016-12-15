# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0049_activity_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='young',
            field=models.BooleanField(default=False, help_text='Onko tämä tunti lapsille?'),
            preserve_default=False,
        ),
    ]
