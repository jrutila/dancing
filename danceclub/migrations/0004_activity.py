# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0003_auto_20160112_0745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('type', models.CharField(help_text='Tekninen nimi, joka kertoo minkä otsikon alle tapahtumat tulevat', max_length=10)),
                ('name', models.CharField(help_text='Nimi, joka näytetään ilmoittautujille', max_length=200)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('when', models.CharField(help_text='Milloin tapahtuu. Esim (To klo 15:00 - 16:00)', max_length=50)),
                ('who', models.CharField(help_text='Kuka vetää?', max_length=200)),
            ],
        ),
    ]
