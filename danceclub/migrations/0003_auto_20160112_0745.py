# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0002_auto_20160111_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='couple',
            name='age_level',
            field=models.CharField(choices=[('L1', 'Lapsi I'), ('L2', 'Lapsi II'), ('J1', 'Juniori I'), ('J2', 'Juniori II'), ('N', 'Nuoriso'), ('Y', 'Yleinen'), ('S1', 'Seniori I'), ('S2', 'Seniori II'), ('S3', 'Seniori III'), ('S4', 'Seniori IV')], default=0, max_length=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='couple',
            name='ended',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dancer',
            name='license',
            field=models.CharField(blank=True, null=True, max_length=20),
        ),
    ]
