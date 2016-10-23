# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('common', '0008_competitionpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitionpage',
            name='enroll_help',
            field=cms.models.fields.PlaceholderField(editable=False, to='cms.Placeholder', null=True, slotname='enroll_help', related_name='competition_enroll_help'),
        ),
    ]
