from django.db import models
from django.contrib.auth.models import User

LEVELS = (('F', 'F'), ('E', 'E'), ('D', 'D'), ('C','C'), ('B','B'), ('A', 'A'))
AGES = (('L1', 'Lapsi I'), ('L2', 'Lapsi II'), ('J1', 'Juniori I'), ('J2','Juniori II'), ('N','Nuoriso'), ('Y', 'Yleinen'), ('S1', 'Seniori I'),
        ('S2', 'Seniori II'), ('S3', 'Seniori III'), ('S4', 'Seniori IV'))

class Member(models.Model):
    user = models.ForeignKey(User)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Dancer(Member):
    license = models.CharField(max_length=20, null=True, blank=True)

class Couple(models.Model):
    man = models.ForeignKey(Dancer, related_name='man')
    woman = models.ForeignKey(Dancer, related_name='woman')

    started = models.DateField()
    ended = models.DateField(blank=True, null=True)

    level = models.CharField(max_length=1, choices=LEVELS)
    age_level = models.CharField(max_length=2, choices=AGES)
    points = models.PositiveIntegerField()

    def __str__(self):
        return "%s - %s (%s %s)" % (str(self.man), str(self.woman), str(self.age_level), str(self.level))
