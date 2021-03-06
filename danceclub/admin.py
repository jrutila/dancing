from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Member, Dancer, Couple, Activity, ActivityParticipation, Transaction, Season, ReferenceNumber, DanceEvent, DanceEventParticipation, OwnCompetition
from .models import CompetitionParticipation
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms
from django.db.models import Sum
from reversion.admin import VersionAdmin
from django.contrib.auth.hashers import make_password
import random
import string
from django.conf.urls import url, include
from datetime import datetime
import time
from django.utils import timezone
from danceclub.views import send_payment_email

def member_saldo(obj):
    return Transaction.objects.filter(owner=obj.member).aggregate(Sum('amount'))['amount__sum']

def saldo(obj):
    return Transaction.objects.filter(owner=obj).aggregate(Sum('amount'))['amount__sum']

class RefNumberInlineForm(forms.ModelForm):
    def has_changed(self):
        return True
    
class ReferenceNumberInline(GenericTabularInline):
    model = ReferenceNumber
    ct_field = "object_type"
    ct_fk_field = "object_id"
    extra = 0
    form = RefNumberInlineForm
    
class TransactionInline(admin.TabularInline):
    model = Transaction

def send_payment_link(modeladmin, request, queryset):
    message = 'Hei,\nOlemme tarkastaneet saatuja maksuja ja näyttää siltä, että sinulla on jotain maksuja suorittamatta.\nOle hyvä ja tarkista maksutietosi osoitteesta: %s\n\nTerveisin,\nTanssiklubi Dancing'
    for m in queryset:
        send_payment_email(request, m, message)

class MemberAdmin(admin.ModelAdmin):
    model = Member
    readonly_fields = ('email',)
    inlines = [ ReferenceNumberInline, TransactionInline ]
    list_display = ('__str__', saldo)
    actions = [send_payment_link]
    
    def email(self, obj):
        return obj.user.email

class DancerCreateForm(forms.ModelForm):
    class Meta:
        exclude = ['user', 'young']
    member = forms.ModelChoiceField(queryset=Member.objects.all())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('instance' in kwargs and kwargs['instance']):
            self.fields['member'].initial = Member.objects.get(user=kwargs['instance'].user)

    # Hack to resave the member as a dancer
    def save(self, commit=True):
        if self.instance.id:
            return super().save(commit)
        else:
            member = self.cleaned_data['member']
            dancer = Dancer(member_ptr_id=member.id)
            dancer.__dict__.update(member.__dict__)
            if commit:
                dancer.save()
            return dancer
        
    def save_m2m(self):
        pass
    
class DancerAdmin(admin.ModelAdmin):
    form = DancerCreateForm

from django.shortcuts import render

class DanceEventsCreationForm(forms.Form):
    date = forms.DateField()
    who = forms.CharField()
    deadline = forms.DateTimeField(required=False)
    public_since = forms.DateTimeField(required=False)
    private_cost = forms.DecimalField()
    public_cost = forms.DecimalField()
    
    privates = forms.CharField(widget=forms.Textarea, help_text="Syötä erillisille riveille kellonajat näin: 1315-1400. Nimeksi tulee 'Yksäri'",required=False)
    publics = forms.CharField(widget=forms.Textarea, help_text="Syötä erillisille riveille kellonajat ja nimi näin: 1400-1445 Ryhmä E-A Vakiot",required=False)
    
    def get_times(self, tim):
        date = self.cleaned_data['date']
        start = tim.split("-")[0].strip()
        end = tim.split("-")[1].strip()
        start = datetime.combine(date, datetime.fromtimestamp(time.mktime(time.strptime(start, "%H%M"))).time())
        end = datetime.combine(date, datetime.fromtimestamp(time.mktime(time.strptime(end, "%H%M"))).time())
        start = timezone.make_aware(start)
        end = timezone.make_aware(end)
        return start,end
        
    def clean_publics(self):
        pu = self.cleaned_data['publics'].split("\n")
        for p in pu:
            if len(p.split(" ",1)) != 2:
                self.add_error("publics", "Kirjoita myös tunnin nimi")
        return self.cleaned_data['publics']
    
    def save(self, commit=True):
        who = self.cleaned_data['who']
        date = self.cleaned_data['date']
        deadline = self.cleaned_data['deadline']
        public_since = self.cleaned_data['public_since']
        private_cost = self.cleaned_data['private_cost']
        public_cost = self.cleaned_data['public_cost']
        publics = self.cleaned_data['publics']
        
        for pr in self.cleaned_data['privates'].split('\n'):
            start,end = self.get_times(pr)
            DanceEvent.objects.update_or_create(
                start=start,
                end=end,
                defaults={
                    "who": who,
                    "name": "Yksäri",
                    "cost": private_cost,
                    "cost_per_participant": False,
                    "public_since": public_since,
                    "deadline": deadline
                }
                )
                
        for pr in self.cleaned_data['publics'].split('\n'):
            tim = pr.split(" ",1)[0]
            name = pr.split(" ",1)[1]
            start,end = self.get_times(tim)
            DanceEvent.objects.update_or_create(
                start=start,
                end=end,
                defaults={
                    "who": who,
                    "name": name,
                    "cost": public_cost,
                    "cost_per_participant": True,
                    "deadline": deadline
                }
                )
    
class DanceEventAdmin(admin.ModelAdmin):
    model = DanceEvent
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^mass_add/$', self.admin_site.admin_view(self.mass_add_view)),
        ]
        return my_urls + urls
        
    def mass_add_view(self, request):
        if request.method == 'POST':
            form = DanceEventsCreationForm(request.POST)
            if form.is_valid():
                form.save()
                # TODO: Redirect
        else:
            form = DanceEventsCreationForm()
            
        return render(request, 'danceclub/admin_form.html', {'form': form})

class CurrentActivities(admin.SimpleListFilter):
    title = "Nykyiset"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ('now', "Nykyiset"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'now':
            return queryset.filter(activity__end__gte=timezone.now())
        return queryset
        
class ActivitiesList(admin.RelatedFieldListFilter):
    def __init__(self, field, request, *args, **kwargs):
        super(ActivitiesList, self).__init__(field, request, *args, **kwargs)
        acts = Activity.objects.current_or_next(also_disabled=True)
        self.lookup_choices = [ (x.id, x) for x in acts ]

class NextCompetition(admin.SimpleListFilter):
    title = "Viimeisin kilpailu"
    parameter_name = "competition"

    def lookups(self, request, model_admin):
        return (
            ('all', "Myös vanhat kilpailut"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset
        latest = OwnCompetition.objects.order_by('start')[0]
        return queryset.filter(competition=latest)

class ActivityParticipationAdmin(VersionAdmin):
    list_filter = (CurrentActivities, ('activity', ActivitiesList),)
    list_display = ('activity', 'member', member_saldo)

def comparts(obj):
    return obj.man + ' - ' + obj.woman
    
from django.http import HttpResponseRedirect
from django.core import serializers
from django.shortcuts import redirect

def list_classes(modeladmin, request, queryset):
    return redirect("list-classes")

class CompetitionParticipationAdmin(VersionAdmin):
    list_filter = (NextCompetition,)
    list_display = (comparts, 'club', 'level', 'number', 'paid')
    list_editable = ['paid']
    #actions = [list_classes]

    def get_changelist_formset(self, request, **kwargs):
        if (request.GET.get('e', None)):
            self.list_editable = ['paid', 'club', 'number']
        else:
            self.list_editable = ['paid']
        formset = super().get_changelist_formset(request, **kwargs)
        return formset

admin.site.register(Member, MemberAdmin)
admin.site.register(Dancer, DancerAdmin)
admin.site.register(DanceEvent, DanceEventAdmin)
admin.site.register(DanceEventParticipation)
admin.site.register(CompetitionParticipation, CompetitionParticipationAdmin)
admin.site.register(Couple)
admin.site.register(Activity)
admin.site.register(ActivityParticipation, ActivityParticipationAdmin)
admin.site.register(Transaction)
admin.site.register(Season)
admin.site.register(ReferenceNumber)
admin.site.register(OwnCompetition)

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["username"] = get_unique_username(self.cleaned_data['first_name'], self.cleaned_data['last_name'], self.cleaned_data['email'])
        del self.errors['password1']
        del self.errors['password2']
        return cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.password = make_password(''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)))
        if commit:
            user.save()
        return user

class UserAdmin(UserAdmin):
    add_form = UserCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', ),
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

from django.db.models.signals import pre_save
def get_unique_username(first_name, last_name, email):
    if email and len(email) <= 30:
        return email
    elif first_name and last_name:
        username = first_name.lower()+"."+last_name.lower()
        return username[:30]
    
def my_callback(sender, **kwargs):
    obj = kwargs['instance']
    if not obj.id and not obj.username:
       username = get_unique_username(obj.first_name, obj.last_name, obj.email) # method that combines first name and last name then query on User model, if record found, will append integer 1 and then query again, until found unique username
       obj.username = username
pre_save.connect(my_callback, sender=User)
