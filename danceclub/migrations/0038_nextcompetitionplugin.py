# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('danceclub', '0037_auto_20160916_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='NextCompetitionPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, to='cms.CMSPlugin', primary_key=True, serialize=False, parent_link=True)),
                ('description', cms.models.fields.PlaceholderField(slotname='description', null=True, related_name='nextcompetition_description', editable=False, to='cms.Placeholder')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
