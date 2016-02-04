# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('filer', '0002_auto_20150606_2003'),
        ('common', '0004_homeslide_slide_page_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='TitleImageExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('extended_object', models.OneToOneField(to='cms.Page', editable=False)),
                ('public_extension', models.OneToOneField(related_name='draft_extension', to='common.TitleImageExtension', null=True, editable=False)),
                ('title_image', filer.fields.image.FilerImageField(related_name='title_image', to='filer.Image', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
