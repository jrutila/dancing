# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0036_remove_owncompetition_tickets'),
    ]

    operations = [
        migrations.AddField(
            model_name='owncompetition',
            name='official_info',
            field=models.URLField(help_text='Linkki kilpailukutsuun', default='http://example.com'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='owncompetition',
            name='official_results',
            field=models.URLField(help_text='Linkki tuloksiin', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='owncompetition',
            name='official_timetable',
            field=models.URLField(help_text='Linkki aikatauluun', null=True, blank=True),
        ),
    ]
