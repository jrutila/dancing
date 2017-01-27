# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0053_auto_20170125_2122'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='mail_message',
            field=models.TextField(help_text='Teksti, joka lähetetään sähköpostiviestillä ilmoittautumisen yhteydessä', null=True, blank=True),
        ),
    ]
