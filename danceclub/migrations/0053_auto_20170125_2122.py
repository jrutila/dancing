# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0052_auto_20170125_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='season',
            field=models.ForeignKey(to='danceclub.Season'),
        ),
    ]
