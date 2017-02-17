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
        if user.is_authenticated() and Dancer.objects.filter(user=user):
            dancer = Dancer.objects.get(user=user)
            couple = Couple.objects.get_couple(dancer)
            choices = [(str(d.id),str(d)) for d in couple]
            # List participation ids. Only those within 2 hours
            #part_member_ids = dict(event.participations.values_list('member__id','created_at'))
            part_member_ids = [d.id for d in couple]
            cancel_member_ids = []
            for p in event.participations.all():
                if p.member.id not in [c.id for c in couple]:
                    if not event.cost_per_participant:
                        part_member_ids = []
                else:
                    cancel_member_ids.append(p.member.id)
                    part_member_ids = [c for c in part_member_ids if c != p.member.id]
            #.filter(created_at__gte=)
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
        else:
            self.fields['email'] = forms.EmailField(required=True)
            self.fields['first_name'] = forms.CharField(required=True)
            self.fields['last_name'] = forms.CharField(required=True)
            
        self.fields['event'].initial = event.id
        
    def clean(self):
        cleaned_data = super().clean()
        if self.event.deadline and self.event.deadline < timezone.now():
            raise forms.ValidationError(
                    "Deadline has passed"
                )
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
    #young = forms.BooleanField(label="Olen alle 18-vuotias",required=False)
    
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

class CompetitionEnrollPairForm(forms.Form):
    level = forms.ChoiceField()
    couple = forms.ChoiceField()
    email = forms.EmailField(required=False, label="Sähköpostiosoite")
    
    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition')
        club = kwargs.pop('club')
        super().__init__(*args, **kwargs)
        choices = competition._meta.get_field('agelevels').choices
        als = [c for c in choices if c[0] in competition.agelevels]
        self.competition = competition
        als.insert(0,('-', '--'))
        self.fields['level'].choices = als
        cpls = [(x[0], x[2]) for x in couples()[club]]
        cpls.insert(0, (0, '--'))
        self.fields['couple'].choices = cpls
    
class CompetitionEnrollForm(forms.Form):
    #club = forms.CharField(max_length=60, required=True, label="Seuran nimi")
    #captcha = forms.CharField(max_length=60, required=True, label="Seuran nimi", help_text="Kirjoita seurasi nimi uudestaan, niin kuin se yläpuolella näkyy, jotta tiedämme ettet ole botti")
    
    enroller_name = forms.CharField(max_length=60, required=True, label="Ilmoittajan nimi")
    enroller_email = forms.EmailField(max_length=60, required=True, label="Ilmoittajan sähköposti")
        
    def __init__(self, competition, *args, **kwargs):
        self.couples = couples()
        self.enrolls = 10
        super().__init__(*args, **kwargs)
        self.fields['club'] = forms.ChoiceField(required=True, label="Seura", choices=[(k,k) for k in sorted(self.couples.keys())])

    def clean(self):
        cleaned_data = super().clean()
        #if 'club' not in cleaned_data or 'captcha' not in cleaned_data or cleaned_data['club'] != cleaned_data['captcha']:
            #self.add_error('captcha', "Seuran nimi pitää olla sama molemmissa kentissä")
        for x in range(1,self.enrolls+1):
            level = cleaned_data['level_%d'%x]
            man = cleaned_data['man_%d'%x]
            woman = cleaned_data['woman_%d'%x]
            errors = []
            failed = False
            if level != '-' and man == '':
                self.add_error('man_%d'%x, 'Pakollinen')
                failed = True
            if level != '-' and woman == '':
                self.add_error('woman_%d'%x, 'Pakollinen')
                failed = True
            if level == '-' and (man != '' or woman != ''):
                self.add_error('level_%d'%x, 'Pakollinen')
                failed = True
            if level == '-' and not failed:
                del cleaned_data['level_%d'%x]
                del cleaned_data['woman_%d'%x]
                del cleaned_data['man_%d'%x]
                del cleaned_data['email_%d'%x]
        return cleaned_data
        
    def save(self):
        cd = self.cleaned_data
        self.parts = []
        for x in range(1,self.enrolls+1):
            if 'level_%d'%x in cd:
                level = cd['level_%d'%x]
                man = cd['man_%d'%x]
                woman = cd['woman_%d'%x]
                email = cd['email_%d'%x]
                part = CompetitionParticipation.objects.create(
                    competition=self.competition,
                    level=level,
                    club=cd['club'],
                    man=man,
                    woman=woman,
                    email=email,
                    enroller_name=cd['enroller_name'],
                    enroller_email=cd['enroller_email']
                    )
                self.parts.append(part)