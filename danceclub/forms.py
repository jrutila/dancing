from django import forms
from .models import Activity, ActivityParticipation, Season
from django.utils import timezone
from .models import Member, Dancer, Couple
from django.contrib.auth.models import User

class CancelForm(forms.Form):
    actpartid = forms.IntegerField(widget=forms.HiddenInput)
    member = forms.CharField(widget=forms.HiddenInput)
    
class LostLinkForm(forms.Form):
    email = forms.EmailField()
    
class DanceEventParticipationForm(forms.Form):
    event = forms.IntegerField(required=True)
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args,**kwargs)
        dancer = Dancer.objects.get(user=user)
        couple = Couple.objects.get_couple(dancer)
        choices = [(str(d.id),str(d.id)) for d in couple]
        self.fields['participant'] = forms.MultipleChoiceField(choices=choices,required=False)
        self.fields['cancel'] = forms.MultipleChoiceField(choices=choices,required=False)
        
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
        member = None
        created = False
        if email:
            try:
                member = Member.objects.get(user__email=email)
                member.user.first_name = first_name
                member.user.last_name = last_name
                member.user.save()
            except Member.DoesNotExist:
                member = None
        if not member:
            try:
                member = Member.objects.get(
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
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'])
            member = Member.objects.create(user=user,young=young)
            created = True
        else:
            member.young = young
            member.save()
        self.member = member
        for act in self.cleaned_data['activities']:
            ActivityParticipation.objects.get_or_create(
                member=member,
                activity=act)
        return member,created

class MassTransactionForm(forms.Form):
    file = forms.FileField()