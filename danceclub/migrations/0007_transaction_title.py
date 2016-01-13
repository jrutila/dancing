# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0006_auto_20160113_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
