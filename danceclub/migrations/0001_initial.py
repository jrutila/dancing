# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Couple',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('started', models.DateField()),
                ('ended', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dancer',
            fields=[
                ('member_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='danceclub.Member', auto_created=True)),
                ('license', models.CharField(max_length=20)),
                ('level', models.CharField(max_length=1, choices=[('F', 'F'), ('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('A', 'A')])),
                ('points', models.PositiveIntegerField()),
            ],
            bases=('danceclub.member',),
        ),
        migrations.AddField(
            model_name='member',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='couple',
            name='man',
            field=models.ForeignKey(related_name='man', to='danceclub.Dancer'),
        ),
        migrations.AddField(
            model_name='couple',
            name='woman',
            field=models.ForeignKey(related_name='woman', to='danceclub.Dancer'),
        ),
    ]
