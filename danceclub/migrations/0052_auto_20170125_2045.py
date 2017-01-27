# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_season(apps, schema_editor):
    Activity = apps.get_model("danceclub", "Activity")
    Season = apps.get_model("danceclub", "Season")
    
    seasons = list(Season.objects.all())
    for a in Activity.objects.filter(season=None):
        s = sorted(seasons, key=lambda s: abs(s.start-a.start)+abs(s.end-a.end))[0]
        a.season = s
        a.save()

class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0051_auto_20170125_2043'),
    ]

    operations = [
        migrations.RunPython(set_season)
    ]
