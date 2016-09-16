# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0032_owncompetition_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='owncompetition',
            name='slug',
            field=models.SlugField(default='default'),
            preserve_default=False,
        ),
    ]
