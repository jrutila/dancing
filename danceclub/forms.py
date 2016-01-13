from django import forms
from .models import Activity
from django.utils import timezone
from .models import Member

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
        try:
            member = Member.objects.get(user__email=email)
        except Member.DoesNotExist:
            try:
                member = Member.objects.get(
                    user__first_name=first_name,
                    user__last_name=last_name)
            except Member.DoesNotExist:
                # Member does not exist! Create one!
                user = User.objects.create(**self.cleaned_data)
                member = Member.objects.create(user=user)
        print(member)