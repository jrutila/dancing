# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0048_owncompetition'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='cost',
            field=models.DecimalField(default='0.00', help_text='Hinta ilman jäsenmaksua 20.00', max_digits=4, decimal_places=2),
            preserve_default=False,
        ),
    ]
