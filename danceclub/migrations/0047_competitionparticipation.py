# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from danceclub.models import AgeLevelField

def fix_levels(apps, schema_editor):
    CompetitionParticipation = apps.get_model("danceclub", "CompetitionParticipation")
    OwnCompetition = apps.get_model("danceclub", "OwnCompetition")
    for p in CompetitionParticipation.objects.all():
        oldlvl = p.level
        p.level = [c[0] for c in AgeLevelField().choices if c[0].endswith(oldlvl)][0]
        p.save()

class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0046_agefield_maxlength'),
    ]

    operations = [
        migrations.RunPython(fix_levels),
    ]
