from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import date
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum, Max, Q
from django.dispatch import receiver
from decimal import *
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Max
from django.core.exceptions import ValidationError
import datetime
import uuid
from collections import defaultdict

LEVELS = (('F', 'F'), ('E', 'E'), ('D', 'D'), ('C','C'), ('B','B'), ('A', 'A'))
COMP_LEVELS = (('CUP', 'C-A Cup'), ('BA', 'B-A'))
AGES = (('L1', 'Lapsi I'), ('L2', 'Lapsi II'), ('J1', 'Juniori I'), ('J2','Juniori II'), ('N','Nuoriso'), ('Y', 'Yleinen'), ('S1', 'Seniori I'),
        ('S2', 'Seniori II'), ('S3', 'Seniori III'), ('S4', 'Seniori IV'))
        
season_cost = Decimal("20.00")
normal_costs = {
    'dancing': [Decimal("80.00"), Decimal("45.00"), Decimal("35.00")],
    '*': [Decimal("55.00"), Decimal("45.00"), Decimal("35.00")],
    }
    
youth_costs = {
    '*': [Decimal("5.00"), Decimal("10.00"), Decimal("5.00")],
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
        
class MemberManager(models.Manager):
    def get_or_create(self, email, first_name, last_name, defaults={'young': False}):
        member = None
        created = False
        if email:
            try:
                member = self.get(user__email=email)
                member.user.first_name = first_name
                member.user.last_name = last_name
                member.user.save()
            except Member.DoesNotExist:
                member = None
        if not member:
            try:
                member = self.get(
                        user__first_name=first_name,
                        user__last_name=last_name,
                        user__email='')
                if email:
                    member.user.email = email
                    member.user.save()
            except Member.DoesNotExist:
                member = None
        if not member:
            # Member does not exist! Create one!
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email)
            member = self.create(user=user,**defaults)
            created = True
        return member,created

class Member(models.Model):
    user = models.ForeignKey(User)
    reference_numbers = GenericRelation(ReferenceNumber, content_type_field='object_type')
    token = models.UUIDField(unique=True,blank=False,null=False,default=uuid.uuid4, editable=False)
    young = models.BooleanField(help_text="Olen alle 16-vuotias",blank=True)
    
    objects = MemberManager()

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return self.user.first_name + " " + self.user.last_name
        elif self.user.email:
            return self.user.email
        return "Vierailija"
            
    
    def get_absolute_url(self):
        from .views import get_member_url
        return get_member_url(self)
        
@receiver(post_save, sender=Member)
def create_refnumber(instance, created, **kwargs):
    if created:
        ReferenceNumber.objects.create(
            object=instance)

class Dancer(Member):
    license = models.CharField(max_length=20, null=True, blank=True)
    
class CoupleManager(models.Manager):
    def get_couple(self, dancer):
        return self.filter(Q(man=dancer) | Q(woman=dancer)).filter(ended__isnull=True).first()

class Couple(models.Model):
    man = models.ForeignKey(Dancer, related_name='man')
    woman = models.ForeignKey(Dancer, related_name='woman')

    started = models.DateField()
    ended = models.DateField(blank=True, null=True)

    level_standard = models.CharField(max_length=1, choices=LEVELS, null=True, blank=True)
    points_standard = models.PositiveIntegerField(null=True, blank=True)
    level_latin = models.CharField(max_length=1, choices=LEVELS, null=True, blank=True)
    points_latin = models.PositiveIntegerField(null=True, blank=True)
    age_level = models.CharField(max_length=2, choices=AGES)
    
    objects = CoupleManager()

    def __str__(self):
        if (self.level_standard == None and self.level_latin == None):
            level = ""
        elif (self.level_latin == None or self.level_standard <= self.level_latin):
            level = self.level_standard
        else:
            level = self.level_latin
        return "%s - %s (%s %s)" % (str(self.man), str(self.woman), str(self.age_level), str(level))
        
    def __iter__(self):
        yield self.man
        yield self.woman

class ActivityManager(models.Manager):
    def current_or_next(self, also_disabled=False):
        curr_season = Season.objects.current_season()
        next_season = Season.objects.next_season()
        if not curr_season and not next_season:
            return self.filter(start__gte=timezone.now())
        f = self.filter(
            start__gte=curr_season.start if curr_season else next_season.start,
            end__lte=next_season.end if next_season else curr_season.end)
        if (not also_disabled):
            f = f.filter(active=True)
        return f.order_by('start')

class Activity(models.Model):
    type = models.CharField(max_length=10,help_text="Tekninen nimi, joka kertoo minkä otsikon alle tapahtumat tulevat")
    name = models.CharField(max_length=200, help_text="Nimi, joka näytetään ilmoittautujille")
    start = models.DateField()
    end = models.DateField()
    when = models.CharField(max_length=50, help_text="Milloin tapahtuu. Esim (To klo 15:00 - 16:00)")
    who = models.CharField(max_length=200, help_text="Kuka vetää?")
    active = models.BooleanField(default=True, help_text="Ota täppä pois jos haluat pois päältä")
    message = models.TextField(help_text="Teksti, joka näytetään ilmoittautumisen yhteydessä", null=True, blank=True)

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
    cost = models.DecimalField(decimal_places=2, max_digits=6)
    cost_per_participant = models.BooleanField(help_text="Valitse tämä, jos maksu on per osallistuja")
    public_since = models.DateTimeField(help_text="Mistä hetkestä eteenpäin vapaasti varattavissa", blank=True, null=True)
    deadline = models.DateTimeField(help_text="Ilmoittautumaan pystyy ennen tätä hetkeä", blank=True, null=True)
    
    def __str__(self):
        return "%s: %s - %s" % (self.who, self.name, timezone.get_current_timezone().normalize(self.start))
    
class DanceEventParticipation(models.Model):
    event = models.ForeignKey(DanceEvent,related_name='participations')
    member = models.ForeignKey(Member)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return "%s - %s" % (str(self.member), str(self.event))
    
    class Meta:
        permissions = (
            ("view_danceeventparticipation", "Can see all dance event participations"),
        )
        
@receiver(post_save, sender=DanceEventParticipation)
@receiver(post_delete, sender=DanceEventParticipation)
def create_event_transaction(instance, **kwargs):
    cost = -1*instance.event.cost
    event = instance.event
    member = instance.member
    created_at = instance.created_at
    event_name = instance.event.name
    if not 'created' in kwargs:
        #DELETE
        tr = Transaction.objects.filter(
            source_type=ContentType.objects.get_for_model(event),
            source_id=event.id,
            owner=member)
        tr.delete()
        
    if cost < Decimal('0.00'):
        if not event.cost_per_participant:
            parts = DanceEventParticipation.objects.filter(event=event)
            cost = cost/parts.count() if parts.count() > 0 else None
            for part in parts:
                member = part.member
                created_at = part.created_at
                tr,cr = Transaction.objects.update_or_create(
                    source_type=ContentType.objects.get_for_model(event),
                    source_id=event.id,
                    owner=member,
                    defaults={
                    'amount': cost,
                    'created_at': created_at,
                    'title': "%s" % str(event)})
        if 'created' in kwargs:
            if event.cost_per_participant:
                tr,cr = Transaction.objects.update_or_create(
                    source_type=ContentType.objects.get_for_model(event),
                    source_id=event.id,
                    owner=member,
                    defaults={
                    'amount': cost,
                    'created_at': created_at,
                    'title': "%s" % str(event)})

@receiver(post_save, sender=ActivityParticipation)
@receiver(post_delete, sender=ActivityParticipation)
def set_activity_transactions(instance, **kwargs):
    season = Season.objects.get_season(instance.activity)
    owner = instance.member
    acts = ActivityParticipation.objects.filter(
        member=instance.member,
        activity__start__gte=season.start,
        activity__end__lte=season.end).order_by('-activity__type')
    Transaction.objects.filter(
        owner=instance.member,
        source_type=ContentType.objects.get_for_model(Activity),
        source_id=instance.activity.id
    ).delete()
    
    if 'created' in kwargs:
        Transaction.objects.get_or_create(
            source_type=ContentType.objects.get_for_model(season),
            source_id=season.id,
            owner=owner,
            defaults={
            'amount':-1*season_cost,
            'created_at':instance.created_at,
            'title':"Jäsenmaksu %s" % str(season)
            })
        Transaction.objects.create(
            source=instance.activity,
            owner=instance.member,
            amount = Decimal('0.00'),
            created_at = instance.created_at,
            title = "%s (%s)" % (instance.activity.name, str(season)))
        
    if len(acts) == 0 and not 'created' in kwargs:
        # If all deleted
        Transaction.objects.filter(
            owner=instance.member,
            source_type=ContentType.objects.get_for_model(season),
            source_id=season.id).delete()
    else:
        trans = Transaction.objects.filter(
            owner=instance.member,
            source_type=ContentType.objects.get_for_model(Activity),
            source_id__in=[x.activity.id for x in acts])
        ids = [x.activity.id for x in acts]
        trans = sorted(trans, key=lambda x: ids.index(x.source.id))
        
        i = 0
        cost = normal_costs
        if owner.young:
            cost = youth_costs
            
        for t in trans:
            key = t.source.type
            if key not in cost:
                key = '*'
            t.amount = -1*cost[key][i]
            if i < len(cost):
                i = i + 1;
            t.save()

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
        return self.filter(start__lte=timezone.now(), end__gte=timezone.now()).first()
        
    def next_season(self):
        return self.filter(start__gte=timezone.now(), end__gte=timezone.now()).order_by("start").first()

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
        
def parse_list(value):
    if type(value) is list:
        return " ".join(value)
    vals = value.split(" ")
    return vals
    
class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError('You must select a maximum of %s choice%s.'
                    % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value
        
from django.contrib.admin.widgets import FilteredSelectMultiple
class AgeLevelField(models.Field):
    #__metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        c=[]
        for ak,ad in AGES:
            for lk, ld in LEVELS+COMP_LEVELS:
                if lk not in ['F', 'E', 'D']:
                    for sk,sd in [('ltn', 'Latin'), ('std', 'Vakio'), ('all', '10-tanssi')]:
                        c.append(("%s-%s-%s" % (sk,ak,lk), "%s %s %s" % (ad, ld, sd)))
                else:
                    c.append(("all-%s-%s" % (ak,lk), "%s %s" % (ad, ld)))
        kwargs["choices"] = c
        super(AgeLevelField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return models.TextField().db_type(connection)
        
    def get_db_prep_save(self, value, connection):
        return " ".join(value)
        
    def validate(self, value, model_instance):
        return
        
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return parse_list(value)
    """
            
        
    def to_python(self, value):
        print("topython")
        if value is None:
            return value
        return [x for x in self.choices if x[0] in value]
        #return parse_list(value)
        
    def get_prep_value(self, value):
        print("prep value")
        return ' '.join(value)
        
    """
    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank,
                    'label': self.verbose_name, 
                    'help_text': self.help_text,
                    'choices':self.choices
        }
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults["widget"] = FilteredSelectMultiple("Age levels", False, attrs={'rows': '10'})
        defaults.update(kwargs)
        return forms.MultipleChoiceField(**defaults)
        
class Competition(models.Model):
    class Meta:
        abstract = True
    date = models.DateField()
    name = models.CharField(max_length=500)
    
class OtherCompetition(Competition):
    # If arranger is null, it is our own competition
    city = models.CharField(max_length=30)
    arranger = models.CharField(max_length=500, null=True, blank=True, help_text="Jätä tyhjäksi, jos kyseessä omat kisat")
    link = models.URLField(null=True,blank=True)
    
class OwnCompetition(Competition):
    slug = models.SlugField()
    start = models.TimeField(null=True, blank=True, help_text="Etusivua varten, kun asetettu, laskuri tulee etusivulle")
    deadline = models.DateTimeField(help_text="Mihin asti saa ilmoittautua netin kautta")
    
    official_info = models.URLField(help_text="Linkki kilpailukutsuun")
    official_timetable = models.URLField(help_text="Linkki aikatauluun", null=True, blank=True)
    official_results = models.URLField(help_text="Linkki tuloksiin", null=True, blank=True)
    
    cost = models.DecimalField(decimal_places=2, max_digits=6, help_text="Hinta per pari")
    cost_after_deadline = models.DecimalField(decimal_places=2, max_digits=6, help_text="Hinta deadlinen jälkeen")
    cost_deadline = models.DateTimeField()
    
    agelevels = AgeLevelField()
    
    place_name = models.CharField(max_length=50, help_text="Paikan nimi")
    address = models.CharField(max_length=50, help_text="Osoite")
