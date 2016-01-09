# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('common', '0002_auto_20160109_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='homeslide',
            name='slide_image',
            field=filer.fields.image.FilerImageField(to='filer.Image', default=-1, related_name='slide_image'),
            preserve_default=False,
        ),
    ]
