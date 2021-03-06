# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-27 06:22
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0059_dancer_social'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dancer',
            name='license',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Lisenssinumero'),
        ),
        migrations.AlterField(
            model_name='dancer',
            name='social',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Hetun loppuosa'),
        ),
        migrations.AlterField(
            model_name='member',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, verbose_name='Puhelinnumero'),
        ),
    ]
