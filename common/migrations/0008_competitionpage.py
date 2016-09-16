# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('danceclub', '0034_owncompetition_place_name'),
        ('common', '0007_auto_20160317_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitionPage',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('competition', models.ForeignKey(to='danceclub.OwnCompetition')),
                ('description', cms.models.fields.PlaceholderField(to='cms.Placeholder', related_name='competition_description', editable=False, null=True, slotname='description')),
                ('tickets', cms.models.fields.PlaceholderField(to='cms.Placeholder', related_name='competition_tickets', editable=False, null=True, slotname='tickets')),
            ],
        ),
    ]
