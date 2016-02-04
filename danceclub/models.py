from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import *
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Max
from django.core.exceptions import ValidationError
import datetime
import uuid

LEVELS = (('F', 'F'), ('E', 'E'), ('D', 'D'), ('C','C'), ('B','B'), ('A', 'A'))
AGES = (('L1', 'Lapsi I'), ('L2', 'Lapsi II'), ('J1', 'Juniori I'), ('J2','Juniori II'), ('N','Nuoriso'), ('Y', 'Yleinen'), ('S1', 'Seniori I'),
        ('S2', 'Seniori II'), ('S3', 'Seniori III'), ('S4', 'Seniori IV'))
        
season_cost = Decimal("20.00")
costs = {
    'dancing': [Decimal("80.00"), Decimal("45.00"), Decimal("35.00")],
    '*': [Decimal("55.00"), Decimal("45.00"), Decimal("35.00")],
    }
    
def get_max_ref():
    m = ReferenceNumber.objects.all().aggregate(Max('number'))['number__max']
    if not m:
        m = 9000000
    m = int(m/10)
    m = m+1
    return m*10+reference_check_number(str(m))
        
def reference_check_number(ref):
    multipliers = (7, 3, 1)
    ref = ref.replace(' ', '')
    inverse = map(int, ref[::-1])
    summ = sum(multipliers[i % 3] * x for i, x in enumerate(inverse))
    return (10 - (summ % 10)) % 10

def validate_ref(value):
    ch = value % 10
    m = int(value/10)
    r = reference_check_number(str(m))
    if r != ch:
        raise ValidationError('%s is not a valid reference number (should be %s)' % (value,m*10+r))
    
class ReferenceNumber(models.Model):
    number = models.PositiveIntegerField(
        unique=True,
        default=get_max_ref,
        validators=[validate_ref])
    
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('object_type', 'object_id')
    
    def __str__(self):
        return "%s: %s" % (self.number, str(self.object))

class Member(models.Model):
    user = models.ForeignKey(User)
    reference_numbers = GenericRelation(ReferenceNumber, content_type_field='object_type')
    token = models.UUIDField(unique=True,blank=False,null=False,default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
        
@receiver(post_save, sender=Member)
def create_refnumber(instance, created, **kwargs):
    if created:
        ReferenceNumber.objects.create(
            object=instance)

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

class ActivityManager(models.Manager):
    def current_or_next(self):
        season = Season.objects.current_or_next_season()
        return self.filter(start__gte=season.start, end__lte=season.end)

class Activity(models.Model):
    type = models.CharField(max_length=10,help_text="Tekninen nimi, joka kertoo minkä otsikon alle tapahtumat tulevat")
    name = models.CharField(max_length=200, help_text="Nimi, joka näytetään ilmoittautujille")
    start = models.DateField()
    end = models.DateField()
    when = models.CharField(max_length=50, help_text="Milloin tapahtuu. Esim (To klo 15:00 - 16:00)")
    who = models.CharField(max_length=200, help_text="Kuka vetää?")

    objects = ActivityManager()
    
    def __str__(self):
        s = "%s %s" % (self.name, self.when)
        if self.end < date.today():
            s = s + " (päättynyt: %s)" % self.end
        return s
        
class ActivityParticipationManager(models.Manager):
    def filter_canceable(self, member):
        return self.filter(member=member, created_at__gte=(timezone.now()-datetime.timedelta(days=14)))
        
class ActivityParticipation(models.Model):
    activity = models.ForeignKey(Activity)
    member = models.ForeignKey(Member, related_name='activities')
    
    created_at = models.DateTimeField(default=timezone.now)
    cancelled = models.BooleanField(default=False)
    
    objects = ActivityParticipationManager()
    def __str__(self):
        return "%s - %s" % (str(self.member), str(self.activity))
        
class DanceEvent(models.Model):
    name = models.CharField(max_length=200, help_text="Nimi, joka näytetään ilmoittautujille")
    start = models.DateTimeField()
    end = models.DateTimeField()
    who = models.CharField(max_length=200, help_text="Kuka vetää?")
    extra = models.TextField(help_text="Lisätietoja", blank=True)
    
    def __str__(self):
        return "%s: %s - %s" % (self.who, self.name, timezone.get_current_timezone().normalize(self.start))
    
class DanceEventParticipation(models.Model):
    event = models.ForeignKey(DanceEvent)
    dancer = models.ForeignKey(Dancer)
    
    cancelled = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s - %s" % (str(self.dancer), str(self.event))
        
@receiver(post_delete, sender=ActivityParticipation)
def update_transactions(instance, **kwargs):
    season = Season.objects.get_season(instance.activity)
    acts = ActivityParticipation.objects.filter(
        member=instance.member,
        activity__start__gte=season.start,
        activity__end__lte=season.end)
    Transaction.objects.filter(
        owner=instance.member,
        source_type=ContentType.objects.get_for_model(Activity),
        source_id=instance.activity.id).delete()
        
    if len(acts) == 0:
        Transaction.objects.filter(
            owner=instance.member,
            source_type=ContentType.objects.get_for_model(season),
            source_id=season.id).delete()
    else:
        trans = Transaction.objects.filter(
            owner=instance.member,
            source_type=ContentType.objects.get_for_model(Activity),
            source_id__in=[x.activity.id for x in acts])
        i = 0
        cost = costs["*"]
        for t in trans:
            t.amount = -1*cost[i]
            if i < len(cost)-1: i = i + 1
            t.save()
        
@receiver(post_save, sender=ActivityParticipation)
def create_transactions(instance, created, **kwargs):
    if created:
        season = Season.objects.get_season(instance.activity)
        try:
            tr = Transaction.objects.get(
                source_type=ContentType.objects.get_for_model(season),
                source_id=season.id,
                owner=instance.member)
        except Transaction.DoesNotExist:
            tr = Transaction.objects.create(
                source=season,
                owner=instance.member,
                amount = -1*season_cost,
                created_at = instance.created_at,
                title = 'Jäsenmaksu %s' % str(season))
        try:
            tr = Transaction.objects.get(
                source_type=ContentType.objects.get_for_model(instance.activity),
                source_id=instance.activity.id,
                owner=instance.member)
        except Transaction.DoesNotExist:
            acts = ActivityParticipation.objects.filter(
                member=instance.member,
                activity__start__gte=season.start,
                activity__end__lte=season.end).count()
            cost = costs["*"][acts-1]
            tr = Transaction.objects.create(
                source=instance.activity,
                owner=instance.member,
                amount = -1*cost,
                created_at = instance.created_at,
                title = "%s (%s)" % (instance.activity.name, str(season)))


class AlreadyExists(BaseException):
    pass

class TransactionManager(models.Manager):
    def add_transaction(self, **kwargs):
        source = ReferenceNumber.objects.get(number=kwargs['ref'])
        ref_obj = source.object
        kwargs['source_type'] = ContentType.objects.get_for_model(source)
        kwargs['source_id'] = source.id
        del kwargs['ref']
        if isinstance(ref_obj, Member):
            kwargs['owner'] = ref_obj
        tr,created = Transaction.objects.get_or_create(**kwargs)
        if not created:
            raise AlreadyExists
        return tr

class Transaction(models.Model):
    title = models.CharField(max_length=255, blank=True)
    
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    owner = models.ForeignKey(Member)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    source_type = models.ForeignKey(ContentType, null=True, blank=True)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey('source_type', 'source_id')

    objects = TransactionManager()
    
    def __str__(self):
        return "%s %s %s" % (str(self.owner), str(self.amount), str(self.title))
    
class SeasonManager(models.Manager):
    def current_season(self):
        return self.get(start__lte=timezone.now(), end__gte=timezone.now())

    def current_or_next_season(self):
        return self.filter(end__gte=timezone.now()).order_by("start").first()

    def get_season(self, act):
        return self.get(start__lte=act.start, end__gte=act.end)
        
class Season(models.Model):
    name = models.CharField(max_length=300)
    
    start = models.DateField()
    end = models.DateField()
    
    objects = SeasonManager()
    
    def __str__(self):
        return self.name
        
