from django import forms
from .models import Activity, ActivityParticipation, Season
from django.utils import timezone
from .models import Member, Dancer, Couple, DanceEvent, DanceEventParticipation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
import datetime

class CancelForm(forms.Form):
    actpartid = forms.IntegerField(widget=forms.HiddenInput)
    member = forms.CharField(widget=forms.HiddenInput)
    
class LostLinkForm(forms.Form):
    email = forms.EmailField()
    
class DanceEventParticipationForm(forms.Form):
    event = forms.IntegerField(required=True, widget=forms.HiddenInput())
    
    def __init__(self, user, event, *args, **kwargs):
        super().__init__(*args,**kwargs)
        last_change = timezone.now()-datetime.timedelta(hours=2)
        self.event = event
        self.user = user
        if user.is_authenticated():
            if user.has_perm("danceclub.add_danceeventparticipation"):
                # Admin can add any dancer
                dancers = Dancer.objects.all()
                part_member_ids = [d.id for d in dancers]
                choices = [(str(d.id), str(d)) for d in dancers]
                self.fields['participant'] = forms.MultipleChoiceField(
                    choices=[c for c in choices if int(c[0]) in part_member_ids],
                    required=False,
                    widget=forms.CheckboxSelectMultiple,
                    label="Ilmoita seuraavat osallistujat")
            elif Dancer.objects.filter(user=user):
                dancer = Dancer.objects.get(user=user)
                couple = Couple.objects.get_couple(dancer)
                choices = [(str(d.id),str(d)) for d in couple or [dancer]]
                # List participation ids. Only those within 2 hours
                #part_member_ids = dict(event.participations.values_list('member__id','created_at'))
                part_member_ids = [d.id for d in couple or [dancer]]
                cancel_member_ids = []
                for p in event.participations.all():
                    if p.member.id not in [c.id for c in couple or [dancer]]:
                        if not event.cost_per_participant:
                            part_member_ids = []
                    else:
                        cancel_member_ids.append(p.member.id)
                        part_member_ids = [c for c in part_member_ids if c != p.member.id]
                self.fields['participant'] = forms.MultipleChoiceField(
                    choices=[c for c in choices if int(c[0]) in part_member_ids],
                    required=False,
                    widget=forms.CheckboxSelectMultiple,
                    label="Ilmoita seuraavat osallistujat")
                self.fields['cancel'] = forms.MultipleChoiceField(
                    choices=[c for c in choices if int(c[0]) in cancel_member_ids],
                    required=False,
                    widget=forms.CheckboxSelectMultiple,
                    label="Peru seuraavat osallistujat")

            # Authenticated user can also add any outsider but is not required
            self.fields['email'] = forms.EmailField(required=False)
            self.fields['first_name'] = forms.CharField(required=False)
            self.fields['last_name'] = forms.CharField(required=False)
        else:
            # Only outsider participants
            self.fields['email'] = forms.EmailField(required=True)
            self.fields['first_name'] = forms.CharField(required=True)
            self.fields['last_name'] = forms.CharField(required=True)
            
        self.fields['event'].initial = event.id
        
    def clean(self):
        cleaned_data = super().clean()
        """
        if not self.user.has_perm("danceclub.add_danceeventparticipation"):
            if self.event.deadline and self.event.deadline < timezone.now():
                raise forms.ValidationError(
                        "Deadline has passed"
                    )
        """
        return cleaned_data
            
    def update_parts(self):
        parts = self.cleaned_data['participant'] if 'participant' in self.cleaned_data else []
        cancels = self.cleaned_data['cancel'] if 'cancel' in self.cleaned_data else []
        email = self.cleaned_data['email'] if 'email' in self.cleaned_data else None
        
        eid = self.cleaned_data['event']
        event = DanceEvent.objects.get(pk=eid)
        
        rets = []
        usercr = False
        
        if not parts and not cancels and email:
            member, usercr = Member.objects.get_or_create(email, self.cleaned_data['first_name'], self.cleaned_data['last_name'])
            parts = [member]
        
        for p in parts:
            if isinstance(p, Member):
                pp = p
            else:
                pp = Dancer.objects.get(pk=p)
            dep,cr = DanceEventParticipation.objects.get_or_create(
                event=event,
                member=pp
                )
            rets.append(dep)
                
        for c in cancels:
            pp = Dancer.objects.get(pk=c)
            DanceEventParticipation.objects.get(
                event=event,
                member=pp).delete()
                
        return rets, usercr
        
        
class ParticipationForm(forms.Form):
    first_name = forms.CharField(label="Etunimi")
    last_name = forms.CharField(label="Sukunimi")
    locality = forms.CharField(label="Kotipaikkakunta")
    email = forms.EmailField(label="Sähköpostiosoite", required=False, help_text="Saat sähköpostiisi maksamiseen liittyvät ohjeet. Jos sinulla ei ole sähköpostia, ilmoittaudu ilman sähköpostia.")
    phone_number = PhoneNumberField(label="Puhelinnumero", required=False, help_text="Vapaaehtoinen tieto. Jätä puhelinnumerosi niin voimme tarvittaessa ottaa sinuun yhteyttä kiireellisissä tapauksissa.")
    birth_year = forms.models.fields_for_model(Member)['birth_year']
    
    activities = forms.ModelMultipleChoiceField(
        label="Tunnit (%s)" % str(Season.objects.current_or_next_season()),
        queryset=Activity.objects.current_or_next(),
        widget=forms.CheckboxSelectMultiple)
        
    def save(self, commit=True):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        locality = self.cleaned_data['locality']
        email = self.cleaned_data['email']
        #young = self.cleaned_data['young']
        member, created = Member.objects.get_or_create(
            email, first_name, last_name)
        member.locality = locality
        member.phone_number = self.cleaned_data['phone_number']
        member.birth_year = self.cleaned_data['birth_year']
        
        for act in self.cleaned_data['activities']:
            member.young = act.young
            
            ActivityParticipation.objects.get_or_create(
                member=member,
                activity=act)
                
        member.save()
        self.member = member
        return member,created

class MassTransactionForm(forms.Form):
    file = forms.FileField()
    
from .models import CompetitionParticipation

import csv
import urllib3
from django.core.cache import cache
from collections import defaultdict
from django.forms import formset_factory, BaseFormSet
from django.utils.functional import cached_property

def couples():
    couples = cache.get('couples', False)
    if not couples:
        url = 'https://onedance.tanssiurheilu.fi/parit'
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        daatta = r.data
        daatta = daatta.decode('latin-1').splitlines()
        spamreader = csv.reader(daatta, delimiter=',', quotechar='"')
        pairs = defaultdict(lambda: [])
        for row in spamreader:
            key = "%s, %s" % (row[3].strip(), row[4].strip())
            pairs[key].append(row)
        couples = pairs
    return couples
    
'''
class CompetitionEnrollFormSet(BaseFormSet):
    @cached_property
    def forms(self):
        """
        Instantiate forms at first property access.
        """
        # DoS protection is included in total_form_count()
        #forms = [self._construct_form(i, competition=self.competition, club=self.club, **self.kwargs) for i in range(self.total_form_count())]
        forms = [self._construct_form(i, competition=self.competition, **self.kwargs) for i in range(self.total_form_count())]
        return forms
'''

class CompetitionEnrollPairForm(forms.Form):
    level = forms.ChoiceField(required=True)
    couple = forms.ChoiceField(required=True)
    email = forms.EmailField(required=False, label="Sähköpostiosoite")
    
    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition')
        club = kwargs.pop('club')
        super().__init__(*args, **kwargs)
        '''
        choices = competition._meta.get_field('agelevels').choices
        als = [c for c in choices if c[0] in competition.agelevels]
        self.competition = competition
        als.insert(0,('-', '--'))
        self.fields['level'].choices = als
        cpls = [(x[0], x[2]) for x in couples()[club]]
        cpls.insert(0, (0, '--'))
        self.fields['couple'].choices = cpls
        '''
        
class CompetitionEnrollFormOnlyClub(forms.Form):
    club =  forms.ChoiceField(required=True, label="Seura")
    
    def __init__(self, competition, *args, **kwargs):
        self.couples = couples()
        self.competition = competition
        super().__init__(*args, **kwargs)
        self.fields['club'].choices = [(k,k) for k in sorted(self.couples.keys())]
    
class CompetitionEnrollForm(CompetitionEnrollFormOnlyClub):
    #club = forms.CharField(max_length=60, required=True, label="Seuran nimi")
    #captcha = forms.CharField(max_length=60, required=True, label="Seuran nimi", help_text="Kirjoita seurasi nimi uudestaan, niin kuin se yläpuolella näkyy, jotta tiedämme ettet ole botti")
    
    enroller_name = forms.CharField(max_length=60, required=False, label="Ilmoittajan nimi")
    enroller_email = forms.EmailField(max_length=60, required=False, label="Ilmoittajan sähköposti")
        
    def __init__(self, competition, club, *args, **kwargs):
        self.enrolls = 10
        
        self.formset = formset_factory(
            CompetitionEnrollPairForm,
            #formset=CompetitionEnrollFormSet,
            extra=10,
            form_kwargs={'competition': competition, 'club': club})
        self.formset.competition = competition
        self.formset.club = club
        if 'data' in kwargs:
            self.formset.kwargs = kwargs['data']
            self.formset = self.formset(kwargs['data'])
        super().__init__(competition, *args, **kwargs)
        self.fields['enroller_name'].required=True
        self.fields['enroller_email'].required=True
        
    def clean(self):
        mycl = super().clean() 
        fs = self.formset
        fscl = self.formset.clean()
        nerr = self.formset.non_form_errors()
        err = self.formset.errors
        Kekkonen
        
    def is_valid(self):
        return super().is_valid() and self.formset.is_valid()
        
    def save(self, commit=True):
        fs = self.formset
        Apron
