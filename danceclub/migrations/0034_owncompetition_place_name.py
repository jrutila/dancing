# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0033_owncompetition_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='owncompetition',
            name='place_name',
            field=models.CharField(help_text='Paikan nimi', default='paikka', max_length=50),
            preserve_default=False,
        ),
    ]
