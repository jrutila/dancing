# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0012_auto_20160118_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='danceevent',
            name='extra',
            field=models.TextField(help_text='Lisätietoja', default=''),
            preserve_default=False,
        ),
    ]
