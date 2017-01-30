# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0054_activity_mail_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='locality',
            field=models.CharField(default='unset', max_length=50),
            preserve_default=False,
        ),
    ]
