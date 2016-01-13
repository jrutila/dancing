# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0007_transaction_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 13, 10, 7, 36, 325331, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='source_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='source_type',
            field=models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType'),
        ),
    ]
