# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('danceclub', '0004_activity'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityParticipation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('cancelled', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(to='danceclub.Activity')),
                ('member', models.ForeignKey(to='danceclub.Member')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('source_id', models.PositiveIntegerField()),
                ('source_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
    ]
