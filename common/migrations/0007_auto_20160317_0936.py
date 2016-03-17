# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import common.models
import filer.fields.image
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('filer', '0002_auto_20150606_2003'),
        ('common', '0006_namecolor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(to='cms.CMSPlugin', serialize=False, primary_key=True, parent_link=True, auto_created=True)),
                ('activity_title', models.CharField(max_length=50, default='Moi')),
                ('activity_subtitle', models.CharField(max_length=50, default='Moi')),
                ('activity_text', models.CharField(max_length=300, default='Moi')),
                ('activity_image', filer.fields.image.FilerImageField(to='filer.Image', related_name='activity_image')),
                ('activity_page_link', cms.models.fields.PageField(to='cms.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AlterField(
            model_name='namecolor',
            name='color',
            field=models.CharField(max_length=10, default=common.models.get_random_color),
        ),
    ]
