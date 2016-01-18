# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import danceclub.models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0011_auto_20160118_1152'),
    ]

    operations = [
        migrations.CreateModel(
            name='DanceEvent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(help_text='Nimi, joka näytetään ilmoittautujille', max_length=200)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('who', models.CharField(help_text='Kuka vetää?', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='DanceEventParticipation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('cancelled', models.BooleanField(default=False)),
                ('dancer', models.ForeignKey(to='danceclub.Dancer')),
                ('event', models.ForeignKey(to='danceclub.DanceEvent')),
            ],
        ),
        migrations.AlterField(
            model_name='referencenumber',
            name='number',
            field=models.PositiveIntegerField(unique=True, validators=[danceclub.models.validate_ref], default=danceclub.models.get_max_ref),
        ),
    ]
