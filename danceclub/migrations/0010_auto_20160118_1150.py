# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0009_auto_20160113_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencenumbers',
            name='number',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
