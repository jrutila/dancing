# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0038_nextcompetitionplugin'),
    ]

    operations = [
        migrations.AddField(
            model_name='nextcompetitionplugin',
            name='competition',
            field=models.ForeignKey(default=1, to='danceclub.OwnCompetition'),
            preserve_default=False,
        ),
    ]
