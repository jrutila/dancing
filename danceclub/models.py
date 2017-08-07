from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import date
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_save
from django.core.signals import request_finished
from django.db.models import Sum, Max, Q
from django.dispatch import receiver
from decimal import *
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Max
from django.core.exceptions import ValidationError
import datetime
import uuid
from collections import defaultdict
from django.core.urlresolvers import reverse
import logging
from phonenumber_field.modelfields import PhoneNumberField
logger = logging.getLogger(__name__)

# DO NOT TOUCH THESE without migration!!
# You will mess the ordering!
LEVELS = (('lek', 'lek'), ('F', 'F'), ('E', 'E'), ('D', 'D'), ('C','C'), ('B','B'), ('A', 'A'))
COMP_LEVELS = (('CUP', 'C-A Cup'), ('BA', 'B-A'))
AGES = (('L1', 'Lapsi I'), ('L2', 'Lapsi II'), ('J1', 'Juniori I'), ('J2','Juniori II'), ('N','Nuoriso'), ('Y', 'Yleinen'), ('S1', 'Seniori I'),
        ('S2', 'Seniori II'), ('S3', 'Seniori III'), ('S4', 'Seniori IV'))
YEAR_CHOICES = [(r,r) for r in range(1900, datetime.date.today().year+1)]
        
season_cost = Decimal("20.00")
normal_costs = {
    'dancing': [Decimal("80.00"), Decimal("45.00"), Decimal("35.00")],
    '*': [Decimal("55.00"), Decimal("45.00"), Decimal("35.00")],
    }
    
youth_costs = {
    '*': [Decimal("5.00"), Decimal("10.00"), Decimal("5.00")],
    }
    
def age_code(level):
    l = level.split('-')
    f = (l[2] if l[2] != "Y" else "YL")+l[3]
    if l[1] == 'all': f = f + "-"
    if l[1] == 'ltn': f = f + "L"
    if l[1] == 'std': f = f + "V"
    return f
    
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
        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip()
        
        member = None
        created = False
        try:
            member = self.get(user__email=email,
                user__first_name=first_name,
                user__last_name=last_name)
        except Member.DoesNotExist:
            member = None
            
        # No member with given email and name combination
        # Try to get the member with null email
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
                
        # Create a new member
        if not member:
            # Member does not exist! Create one!
            username = ('%s-%s-%s' % (email.split('@')[0][:6], email.split('@')[1].replace('.', '')[:6], first_name.replace(' ', '')))[:30]
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username)
            member = self.create(user=user,**defaults)
            created = True
        return member,created

class Member(models.Model):
    user = models.ForeignKey(User)
    locality = models.CharField(max_length=50)
    reference_numbers = GenericRelation(ReferenceNumber, content_type_field='object_type')
    token = models.UUIDField(unique=True,blank=False,null=False,default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(blank=True)
    birth_year = models.IntegerField('Syntymävuosi', blank=True, null=True, choices=YEAR_CHOICES, default=datetime.datetime.now().year)
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

        f = self.filter(season=curr_season or next_season)
        f = f.filter(Q(end__isnull=True) | Q(end__gt=timezone.now()))
        if (not also_disabled):
            f = f.filter(active=True)
        return f.order_by('name')

class Activity(models.Model):
    type = models.CharField(max_length=10,help_text="Tekninen nimi, joka kertoo minkä otsikon alle tapahtumat tulevat")
    name = models.CharField(max_length=200, help_text="Nimi, joka näytetään ilmoittautujille")
    start = models.DateField()
    end = models.DateField()
    season = models.ForeignKey("Season")
    when = models.CharField(max_length=50, help_text="Milloin tapahtuu. Esim (To klo 15:00 - 16:00)")
    who = models.CharField(max_length=200, help_text="Kuka vetää?")
    active = models.BooleanField(default=True, help_text="Ota täppä pois jos haluat pois päältä")
    message = models.TextField(help_text="Teksti, joka näytetään ilmoittautumisen yhteydessä", null=True, blank=True)
    mail_message = models.TextField(help_text="Teksti, joka lähetetään sähköpostiviestillä ilmoittautumisen yhteydessä", null=True, blank=True)
    cost = models.DecimalField(help_text="Hinta ilman jäsenmaksua %s" % season_cost, max_digits=4, decimal_places=2)
    young = models.BooleanField(help_text="Onko tämä tunti lapsille? Ei lisää jäsenmaksua, eli laita koko hinta yläpuolelle!")

    objects = ActivityManager()
    
    def __str__(self):
        s = "%s %s (%s)" % (self.name, self.when, self.season)
        if self.season.end < date.today():
            s = s + " (päättynyt: %s)" % self.season.end
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
        return act.season
        
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
        i=0
        # DO NOT TOUCH THESE without migration!!
        # You will mess the ordering!
        for ak,ad in AGES:
            for lk, ld in LEVELS+COMP_LEVELS:
                if lk == 'lek' and ak not in ['L1', 'L2']:
                    continue
                if (lk not in ['lek','F', 'E', 'D']) or \
                   (lk == 'D' and ak in ['S1', 'S2']) or \
                   (lk in ['E','D'] and ak in ['S3', 'S4']):
                    for sk,sd in [('ltn', 'Latin'), ('std', 'Vakio'), ('all', '10-tanssi' if lk not in ['lek','F','E','D'] else 'Kaikki')]:
                        c.append(("%03d-%s-%s-%s" % (i,sk,ak,lk), "%s %s %s" % (ad, ld, sd)))
                else:
                    c.append(("%03d-all-%s-%s" % (i,ak,lk), "%s %s" % (ad, ld)))
                i=i+1
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
    
    def get_absolute_url(self):
        return reverse('competition_info', kwargs={"slug":self.slug})
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.date)

class CompetitionParticipation(models.Model):
    competition = models.ForeignKey(OwnCompetition, related_name="participations")
    level = models.CharField(max_length=20, choices=OwnCompetition._meta.get_field('agelevels').choices)
    club = models.CharField(max_length=60)
    man = models.CharField(max_length=60)
    woman = models.CharField(max_length=60)
    
    email = models.EmailField(blank=True, null=True)
    reference_number = models.ForeignKey(ReferenceNumber, blank=True, null=True)
    
    enroller_name = models.CharField(max_length=60)
    enroller_email = models.EmailField(max_length=60)
    
    paid = models.BooleanField(default=False)
    number = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return "%s %s: %s - %s" % (
            self.competition,
            [c[1] for c in OwnCompetition._meta.get_field('agelevels').choices if c[0] == self.level][0],
            self.man,
            self.woman
            )
            
    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if instance.number:
            CompetitionParticipation.objects.extra(where=[
                "LOWER(REPLACE(man, ' ', '')) = %s",
                "LOWER(REPLACE(woman, ' ', '')) = %s",
                "LOWER(REPLACE(club, ' ', '')) = %s",
                ], params=[
                    instance.man.replace(" ","").lower(),
                    instance.woman.replace(" ","").lower(),
                    instance.club.replace(" ","").lower()
                ]).update(number=instance.number)

post_save.connect(CompetitionParticipation.post_save, sender=CompetitionParticipation)

@receiver(post_save, sender=CompetitionParticipation)
def create_refnumber(instance, created, **kwargs):
    if created:
        rf = ReferenceNumber.objects.create(
            object=instance)
        instance.reference_number = rf
        instance.save()
        