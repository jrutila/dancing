# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('common', '0009_competitionpage_enroll_help'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitionpage',
            name='sponsors',
            field=cms.models.fields.PlaceholderField(editable=False, to='cms.Placeholder', slotname='sponsors', null=True, related_name='competition_sponsors'),
        ),
    ]
