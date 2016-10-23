# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('danceclub', '0042_competitionparticipation_reference_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionparticipation',
            name='level',
            field=models.CharField(choices=[('all-L1-lek', 'Lapsi I lek'), ('all-L1-F', 'Lapsi I F'), ('all-L1-E', 'Lapsi I E'), ('all-L1-D', 'Lapsi I D'), ('ltn-L1-C', 'Lapsi I C Latin'), ('std-L1-C', 'Lapsi I C Vakio'), ('all-L1-C', 'Lapsi I C 10-tanssi'), ('ltn-L1-B', 'Lapsi I B Latin'), ('std-L1-B', 'Lapsi I B Vakio'), ('all-L1-B', 'Lapsi I B 10-tanssi'), ('ltn-L1-A', 'Lapsi I A Latin'), ('std-L1-A', 'Lapsi I A Vakio'), ('all-L1-A', 'Lapsi I A 10-tanssi'), ('ltn-L1-CUP', 'Lapsi I C-A Cup Latin'), ('std-L1-CUP', 'Lapsi I C-A Cup Vakio'), ('all-L1-CUP', 'Lapsi I C-A Cup 10-tanssi'), ('ltn-L1-BA', 'Lapsi I B-A Latin'), ('std-L1-BA', 'Lapsi I B-A Vakio'), ('all-L1-BA', 'Lapsi I B-A 10-tanssi'), ('all-L2-lek', 'Lapsi II lek'), ('all-L2-F', 'Lapsi II F'), ('all-L2-E', 'Lapsi II E'), ('all-L2-D', 'Lapsi II D'), ('ltn-L2-C', 'Lapsi II C Latin'), ('std-L2-C', 'Lapsi II C Vakio'), ('all-L2-C', 'Lapsi II C 10-tanssi'), ('ltn-L2-B', 'Lapsi II B Latin'), ('std-L2-B', 'Lapsi II B Vakio'), ('all-L2-B', 'Lapsi II B 10-tanssi'), ('ltn-L2-A', 'Lapsi II A Latin'), ('std-L2-A', 'Lapsi II A Vakio'), ('all-L2-A', 'Lapsi II A 10-tanssi'), ('ltn-L2-CUP', 'Lapsi II C-A Cup Latin'), ('std-L2-CUP', 'Lapsi II C-A Cup Vakio'), ('all-L2-CUP', 'Lapsi II C-A Cup 10-tanssi'), ('ltn-L2-BA', 'Lapsi II B-A Latin'), ('std-L2-BA', 'Lapsi II B-A Vakio'), ('all-L2-BA', 'Lapsi II B-A 10-tanssi'), ('all-J1-F', 'Juniori I F'), ('all-J1-E', 'Juniori I E'), ('all-J1-D', 'Juniori I D'), ('ltn-J1-C', 'Juniori I C Latin'), ('std-J1-C', 'Juniori I C Vakio'), ('all-J1-C', 'Juniori I C 10-tanssi'), ('ltn-J1-B', 'Juniori I B Latin'), ('std-J1-B', 'Juniori I B Vakio'), ('all-J1-B', 'Juniori I B 10-tanssi'), ('ltn-J1-A', 'Juniori I A Latin'), ('std-J1-A', 'Juniori I A Vakio'), ('all-J1-A', 'Juniori I A 10-tanssi'), ('ltn-J1-CUP', 'Juniori I C-A Cup Latin'), ('std-J1-CUP', 'Juniori I C-A Cup Vakio'), ('all-J1-CUP', 'Juniori I C-A Cup 10-tanssi'), ('ltn-J1-BA', 'Juniori I B-A Latin'), ('std-J1-BA', 'Juniori I B-A Vakio'), ('all-J1-BA', 'Juniori I B-A 10-tanssi'), ('all-J2-F', 'Juniori II F'), ('all-J2-E', 'Juniori II E'), ('all-J2-D', 'Juniori II D'), ('ltn-J2-C', 'Juniori II C Latin'), ('std-J2-C', 'Juniori II C Vakio'), ('all-J2-C', 'Juniori II C 10-tanssi'), ('ltn-J2-B', 'Juniori II B Latin'), ('std-J2-B', 'Juniori II B Vakio'), ('all-J2-B', 'Juniori II B 10-tanssi'), ('ltn-J2-A', 'Juniori II A Latin'), ('std-J2-A', 'Juniori II A Vakio'), ('all-J2-A', 'Juniori II A 10-tanssi'), ('ltn-J2-CUP', 'Juniori II C-A Cup Latin'), ('std-J2-CUP', 'Juniori II C-A Cup Vakio'), ('all-J2-CUP', 'Juniori II C-A Cup 10-tanssi'), ('ltn-J2-BA', 'Juniori II B-A Latin'), ('std-J2-BA', 'Juniori II B-A Vakio'), ('all-J2-BA', 'Juniori II B-A 10-tanssi'), ('all-N-F', 'Nuoriso F'), ('all-N-E', 'Nuoriso E'), ('all-N-D', 'Nuoriso D'), ('ltn-N-C', 'Nuoriso C Latin'), ('std-N-C', 'Nuoriso C Vakio'), ('all-N-C', 'Nuoriso C 10-tanssi'), ('ltn-N-B', 'Nuoriso B Latin'), ('std-N-B', 'Nuoriso B Vakio'), ('all-N-B', 'Nuoriso B 10-tanssi'), ('ltn-N-A', 'Nuoriso A Latin'), ('std-N-A', 'Nuoriso A Vakio'), ('all-N-A', 'Nuoriso A 10-tanssi'), ('ltn-N-CUP', 'Nuoriso C-A Cup Latin'), ('std-N-CUP', 'Nuoriso C-A Cup Vakio'), ('all-N-CUP', 'Nuoriso C-A Cup 10-tanssi'), ('ltn-N-BA', 'Nuoriso B-A Latin'), ('std-N-BA', 'Nuoriso B-A Vakio'), ('all-N-BA', 'Nuoriso B-A 10-tanssi'), ('all-Y-F', 'Yleinen F'), ('all-Y-E', 'Yleinen E'), ('all-Y-D', 'Yleinen D'), ('ltn-Y-C', 'Yleinen C Latin'), ('std-Y-C', 'Yleinen C Vakio'), ('all-Y-C', 'Yleinen C 10-tanssi'), ('ltn-Y-B', 'Yleinen B Latin'), ('std-Y-B', 'Yleinen B Vakio'), ('all-Y-B', 'Yleinen B 10-tanssi'), ('ltn-Y-A', 'Yleinen A Latin'), ('std-Y-A', 'Yleinen A Vakio'), ('all-Y-A', 'Yleinen A 10-tanssi'), ('ltn-Y-CUP', 'Yleinen C-A Cup Latin'), ('std-Y-CUP', 'Yleinen C-A Cup Vakio'), ('all-Y-CUP', 'Yleinen C-A Cup 10-tanssi'), ('ltn-Y-BA', 'Yleinen B-A Latin'), ('std-Y-BA', 'Yleinen B-A Vakio'), ('all-Y-BA', 'Yleinen B-A 10-tanssi'), ('all-S1-F', 'Seniori I F'), ('all-S1-E', 'Seniori I E'), ('ltn-S1-D', 'Seniori I D Latin'), ('std-S1-D', 'Seniori I D Vakio'), ('all-S1-D', 'Seniori I D Kaikki'), ('ltn-S1-C', 'Seniori I C Latin'), ('std-S1-C', 'Seniori I C Vakio'), ('all-S1-C', 'Seniori I C 10-tanssi'), ('ltn-S1-B', 'Seniori I B Latin'), ('std-S1-B', 'Seniori I B Vakio'), ('all-S1-B', 'Seniori I B 10-tanssi'), ('ltn-S1-A', 'Seniori I A Latin'), ('std-S1-A', 'Seniori I A Vakio'), ('all-S1-A', 'Seniori I A 10-tanssi'), ('ltn-S1-CUP', 'Seniori I C-A Cup Latin'), ('std-S1-CUP', 'Seniori I C-A Cup Vakio'), ('all-S1-CUP', 'Seniori I C-A Cup 10-tanssi'), ('ltn-S1-BA', 'Seniori I B-A Latin'), ('std-S1-BA', 'Seniori I B-A Vakio'), ('all-S1-BA', 'Seniori I B-A 10-tanssi'), ('all-S2-F', 'Seniori II F'), ('all-S2-E', 'Seniori II E'), ('ltn-S2-D', 'Seniori II D Latin'), ('std-S2-D', 'Seniori II D Vakio'), ('all-S2-D', 'Seniori II D Kaikki'), ('ltn-S2-C', 'Seniori II C Latin'), ('std-S2-C', 'Seniori II C Vakio'), ('all-S2-C', 'Seniori II C 10-tanssi'), ('ltn-S2-B', 'Seniori II B Latin'), ('std-S2-B', 'Seniori II B Vakio'), ('all-S2-B', 'Seniori II B 10-tanssi'), ('ltn-S2-A', 'Seniori II A Latin'), ('std-S2-A', 'Seniori II A Vakio'), ('all-S2-A', 'Seniori II A 10-tanssi'), ('ltn-S2-CUP', 'Seniori II C-A Cup Latin'), ('std-S2-CUP', 'Seniori II C-A Cup Vakio'), ('all-S2-CUP', 'Seniori II C-A Cup 10-tanssi'), ('ltn-S2-BA', 'Seniori II B-A Latin'), ('std-S2-BA', 'Seniori II B-A Vakio'), ('all-S2-BA', 'Seniori II B-A 10-tanssi'), ('all-S3-F', 'Seniori III F'), ('ltn-S3-E', 'Seniori III E Latin'), ('std-S3-E', 'Seniori III E Vakio'), ('all-S3-E', 'Seniori III E Kaikki'), ('ltn-S3-D', 'Seniori III D Latin'), ('std-S3-D', 'Seniori III D Vakio'), ('all-S3-D', 'Seniori III D Kaikki'), ('ltn-S3-C', 'Seniori III C Latin'), ('std-S3-C', 'Seniori III C Vakio'), ('all-S3-C', 'Seniori III C 10-tanssi'), ('ltn-S3-B', 'Seniori III B Latin'), ('std-S3-B', 'Seniori III B Vakio'), ('all-S3-B', 'Seniori III B 10-tanssi'), ('ltn-S3-A', 'Seniori III A Latin'), ('std-S3-A', 'Seniori III A Vakio'), ('all-S3-A', 'Seniori III A 10-tanssi'), ('ltn-S3-CUP', 'Seniori III C-A Cup Latin'), ('std-S3-CUP', 'Seniori III C-A Cup Vakio'), ('all-S3-CUP', 'Seniori III C-A Cup 10-tanssi'), ('ltn-S3-BA', 'Seniori III B-A Latin'), ('std-S3-BA', 'Seniori III B-A Vakio'), ('all-S3-BA', 'Seniori III B-A 10-tanssi'), ('all-S4-F', 'Seniori IV F'), ('ltn-S4-E', 'Seniori IV E Latin'), ('std-S4-E', 'Seniori IV E Vakio'), ('all-S4-E', 'Seniori IV E Kaikki'), ('ltn-S4-D', 'Seniori IV D Latin'), ('std-S4-D', 'Seniori IV D Vakio'), ('all-S4-D', 'Seniori IV D Kaikki'), ('ltn-S4-C', 'Seniori IV C Latin'), ('std-S4-C', 'Seniori IV C Vakio'), ('all-S4-C', 'Seniori IV C 10-tanssi'), ('ltn-S4-B', 'Seniori IV B Latin'), ('std-S4-B', 'Seniori IV B Vakio'), ('all-S4-B', 'Seniori IV B 10-tanssi'), ('ltn-S4-A', 'Seniori IV A Latin'), ('std-S4-A', 'Seniori IV A Vakio'), ('all-S4-A', 'Seniori IV A 10-tanssi'), ('ltn-S4-CUP', 'Seniori IV C-A Cup Latin'), ('std-S4-CUP', 'Seniori IV C-A Cup Vakio'), ('all-S4-CUP', 'Seniori IV C-A Cup 10-tanssi'), ('ltn-S4-BA', 'Seniori IV B-A Latin'), ('std-S4-BA', 'Seniori IV B-A Vakio'), ('all-S4-BA', 'Seniori IV B-A 10-tanssi')], max_length=10),
        ),
        migrations.AlterField(
            model_name='couple',
            name='level_latin',
            field=models.CharField(null=True, choices=[('lek', 'lek'), ('F', 'F'), ('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('A', 'A')], max_length=1, blank=True),
        ),
        migrations.AlterField(
            model_name='couple',
            name='level_standard',
            field=models.CharField(null=True, choices=[('lek', 'lek'), ('F', 'F'), ('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('A', 'A')], max_length=1, blank=True),
        ),
    ]
