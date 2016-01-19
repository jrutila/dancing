from django import forms
from .models import Activity, ActivityParticipation
from django.utils import timezone
from .models import Member
from django.contrib.auth.models import User

class CancelForm(forms.Form):
    actpartid = forms.IntegerField(widget=forms.HiddenInput)
    member = forms.CharField(widget=forms.HiddenInput)

class ParticipationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=False, help_text="Saat sähköpostiisi maksamiseen liittyvät ohjeet. Jos sinulla ei ole sähköpostia, pyydä maksuohje salilta.")
    
    activities = forms.ModelMultipleChoiceField(
        queryset=Activity.objects.filter(end__gt=timezone.now()),
        widget=forms.CheckboxSelectMultiple)
        
    def save(self, commit=True):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        member = None
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
            member = Member.objects.create(user=user)
        self.member = member
        for act in self.cleaned_data['activities']:
            ActivityParticipation.objects.get_or_create(
                member=member,
                activity=act)