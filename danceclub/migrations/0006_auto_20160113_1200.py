# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('danceclub', '0005_activityparticipation_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceNumbers',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('object_id', models.PositiveIntegerField()),
                ('object_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='owner',
            field=models.ForeignKey(default=-1, to='danceclub.Member'),
            preserve_default=False,
        ),
    ]
