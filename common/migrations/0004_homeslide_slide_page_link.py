# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('common', '0003_homeslide_slide_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='homeslide',
            name='slide_page_link',
            field=cms.models.fields.PageField(to='cms.Page', default=-1),
            preserve_default=False,
        ),
    ]
