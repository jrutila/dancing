# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0031_othercompetition_owncompetition'),
    ]

    operations = [
        migrations.AddField(
            model_name='owncompetition',
            name='address',
            field=models.CharField(default='Osoite', help_text='Osoite', max_length=50),
            preserve_default=False,
        ),
    ]
