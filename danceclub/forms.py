from django import forms
from .models import Activity, ActivityParticipation, Season
from django.utils import timezone
from .models import Member, Dancer, Couple, DanceEvent, DanceEventParticipation
from django.contrib.auth.models import User
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
        if user.is_authenticated():
            dancer = Dancer.objects.get(user=user)
            couple = Couple.objects.get_couple(dancer)
            choices = [(str(d.id),str(d)) for d in couple]
            # List participation ids. Only those within 2 hours
            part_member_ids = dict(event.participations.values_list('member__id','created_at'))
            #.filter(created_at__gte=)
            self.fields['participant'] = forms.MultipleChoiceField(
                choices=[c for c in choices if int(c[0]) not in part_member_ids],
                required=False,
                widget=forms.CheckboxSelectMultiple)
            self.fields['cancel'] = forms.MultipleChoiceField(
                choices=[c for c in choices if int(c[0]) in part_member_ids and part_member_ids[int(c[0])] >= last_change],
                required=False,
                widget=forms.CheckboxSelectMultiple)
        else:
            self.fields['email'] = forms.EmailField(required=True)
            self.fields['first_name'] = forms.CharField(required=True)
            self.fields['last_name'] = forms.CharField(required=True)
            
        self.fields['event'].initial = event.id
            
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
    email = forms.EmailField(label="Sähköpostiosoite", required=False, help_text="Saat sähköpostiisi maksamiseen liittyvät ohjeet. Jos sinulla ei ole sähköpostia, pyydä maksuohje salilta.")
    young = forms.BooleanField(label="Olen alle 16-vuotias",required=False)
    
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