# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0039_nextcompetitionplugin_competition'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitionParticipation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('level', models.CharField(max_length=10)),
                ('club', models.CharField(max_length=60)),
                ('man', models.CharField(max_length=60)),
                ('woman', models.CharField(max_length=60)),
                ('competition', models.ForeignKey(to='danceclub.OwnCompetition')),
            ],
        ),
    ]
