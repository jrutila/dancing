# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0022_auto_20160302_0748'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='young',
            field=models.BooleanField(default=False, help_text='Olen alle 16-vuotias'),
            preserve_default=False,
        ),
    ]
