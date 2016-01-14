from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import *

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

class Activity(models.Model):
    type = models.CharField(max_length=10,help_text="Tekninen nimi, joka kertoo minkä otsikon alle tapahtumat tulevat")
    name = models.CharField(max_length=200, help_text="Nimi, joka näytetään ilmoittautujille")
    start = models.DateField()
    end = models.DateField()
    when = models.CharField(max_length=50, help_text="Milloin tapahtuu. Esim (To klo 15:00 - 16:00)")
    who = models.CharField(max_length=200, help_text="Kuka vetää?")
    
    def __str__(self):
        s = "%s %s" % (self.name, self.when)
        if self.end < date.today():
            s = s + " (päättynyt: %s)" % self.end
        return s
        
class ActivityParticipation(models.Model):
    activity = models.ForeignKey(Activity)
    member = models.ForeignKey(Member)
    
    cancelled = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s - %s" % (str(self.member), str(self.activity))
        
@receiver(post_save, sender=ActivityParticipation)
def create_transactions(instance, created, **kwargs):
    if created:
        season = Season.objects.get(start__lte=instance.activity.start, end__gte=instance.activity.end)
        try:
            tr = Transaction.objects.get(
                source_type=ContentType.objects.get_for_model(season),
                source_id=season.id,
                owner=instance.member)
        except Transaction.DoesNotExist:
            tr = Transaction.objects.create(
                source=season,
                owner=instance.member,
                amount = Decimal('-25.00'),
                title = 'Jäsenmaksu %s' % str(season))
        
class Transaction(models.Model):
    title = models.CharField(max_length=255, blank=True)
    
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    owner = models.ForeignKey(Member)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    source_type = models.ForeignKey(ContentType, null=True, blank=True)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey('source_type', 'source_id')
    
    def __str__(self):
        return "%s %s %s" % (str(self.owner), str(self.amount), str(self.title))
    
class ReferenceNumbers(models.Model):
    number = models.PositiveIntegerField()
    
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('object_type', 'object_id')
    
class Season(models.Model):
    name = models.CharField(max_length=300)
    
    start = models.DateField()
    end = models.DateField()
    
    def __str__(self):
        return self.name