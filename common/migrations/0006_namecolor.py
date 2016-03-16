# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_titleimageextension'),
    ]

    operations = [
        migrations.CreateModel(
            name='NameColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
    ]
