# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from danceclub.models import AgeLevelField

def fix_levels(apps, schema_editor):
    OwnCompetition = apps.get_model("danceclub", "OwnCompetition")
    for o in OwnCompetition.objects.all():
        agelevels = o.agelevels
        o.agelevels = [] #o.agelevels
        o.save()
        for a in agelevels:
            o.agelevels.append([c[0] for c in AgeLevelField().choices if c[0].endswith(a)][0])
        o.save()

class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0047_competitionparticipation'),
    ]

    operations = [
        migrations.RunPython(fix_levels),
    ]
