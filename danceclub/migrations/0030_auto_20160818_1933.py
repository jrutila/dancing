# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0029_auto_20160517_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='active',
            field=models.BooleanField(help_text='Ota täppä pois jos haluat pois päältä', default=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='message',
            field=models.TextField(help_text='Teksti, joka näytetään ilmoittautumisen yhteydessä', null=True, blank=True),
        ),
    ]
