# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('danceclub', '0010_auto_20160118_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceNumber',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('number', models.PositiveIntegerField(unique=True)),
                ('object_id', models.PositiveIntegerField()),
                ('object_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.RemoveField(
            model_name='referencenumbers',
            name='object_type',
        ),
        migrations.DeleteModel(
            name='ReferenceNumbers',
        ),
    ]
