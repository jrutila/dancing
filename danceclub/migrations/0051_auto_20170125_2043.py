# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0050_activity_young'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='season',
            field=models.ForeignKey(to='danceclub.Season', null=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='activity',
            name='young',
            field=models.BooleanField(help_text='Onko tämä tunti lapsille? Ei lisää jäsenmaksua, eli laita koko hinta yläpuolelle!'),
        ),
    ]
