# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('danceclub', 'member')
    for row in MyModel.objects.all():
        row.token = uuid.uuid4()
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0016_activityparticipation_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='member',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
