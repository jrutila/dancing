from django import forms
from .models import Activity, ActivityParticipation, Season
from django.utils import timezone
from .models import Member, Dancer, Couple, DanceEvent, DanceEventParticipation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
        if user.is_authenticated():
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
    email = forms.EmailField(label="Sähköpostiosoite", required=False, help_text="Saat sähköpostiisi maksamiseen liittyvät ohjeet. Jos sinulla ei ole sähköpostia, ilmoittaudu ilman sähköpostia.")
    young = forms.BooleanField(label="Olen alle 18-vuotias",required=False)
    
    activities = forms.ModelMultipleChoiceField(
        label="Tunnit (%s)" % str(Season.objects.current_or_next_season()),
        queryset=Activity.objects.current_or_next(),
        widget=forms.CheckboxSelectMultiple)
        
    def save(self, commit=True):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        young = self.cleaned_data['young']
        member, created = Member.objects.get_or_create(
            email, first_name, last_name, {'young': young })
        
        if not created and member.young != young:
            member.young = young
            member.save()
            
        for act in self.cleaned_data['activities']:
            ActivityParticipation.objects.get_or_create(
                member=member,
                activity=act)
                
        self.member = member
        return member,created

class MassTransactionForm(forms.Form):
    file = forms.FileField()
    
from .models import CompetitionParticipation
class CompetitionEnrollForm(forms.Form):
    club = forms.CharField(max_length=60, required=True, label="Seuran nimi")
    captcha = forms.CharField(max_length=60, required=True, label="Seuran nimi", help_text="Kirjoita seurasi nimi kahdesti, jotta tiedämme ettet ole botti")
    
    enroller_name = forms.CharField(max_length=60, required=True)
    enroller_email = forms.EmailField(max_length=60, required=True)
        
    def __init__(self, competition, *args, **kwargs):
        self.enrolls = 5
        super().__init__(*args, **kwargs)
        choices = competition._meta.get_field('agelevels').choices
        als = [c for c in choices if c[0] in competition.agelevels]
        self.competition = competition
        als.insert(0,('-', '--'))
        for x in range(1,self.enrolls+1):
            self.fields['level_%d'%x] = forms.ChoiceField(
                choices=als
                )
            self.fields['man_%d'%x] = forms.CharField(max_length=60, required=False)
            self.fields['woman_%d'%x] = forms.CharField(max_length=60, required=False)
            self.fields['email_%d'%x] = forms.EmailField(required=False)
        
    def clean(self):
        cleaned_data = super().clean()
        if 'club' not in cleaned_data or 'captcha' not in cleaned_data or cleaned_data['club'] != cleaned_data['captcha']:
            self.add_error('captcha', "Seuran nimi pitää olla sama molemmissa kentissä")
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
                part = CompetitionParticipation.objects.create(
                    competition=self.competition,
                    level=level,
                    club=cd['club'],
                    man=man,
                    woman=woman
                    )
                self.parts.append(part)