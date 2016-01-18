from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Member, Dancer, Couple, Activity, ActivityParticipation, Transaction, Season, ReferenceNumber, DanceEvent, DanceEventParticipation
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms

class RefNumberInlineForm(forms.ModelForm):
    def has_changed(self):
        return True
    
class ReferenceNumberInline(GenericTabularInline):
    model = ReferenceNumber
    ct_field = "object_type"
    ct_fk_field = "object_id"
    extra = 0
    form = RefNumberInlineForm

class MemberAdmin(admin.ModelAdmin):
    model = Member
    inlines = [ ReferenceNumberInline ]

admin.site.register(Member, MemberAdmin)
admin.site.register(Dancer)
admin.site.register(DanceEvent)
admin.site.register(DanceEventParticipation)
admin.site.register(Couple)
admin.site.register(Activity)
admin.site.register(ActivityParticipation)
admin.site.register(Transaction)
admin.site.register(Season)
admin.site.register(ReferenceNumber)

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["username"] = get_unique_username(self.cleaned_data['first_name'], self.cleaned_data['last_name'])
        del self.errors['password1']
        del self.errors['password2']
        return cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
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
def get_unique_username(first_name, last_name):
    return first_name.lower()+"."+last_name.lower()
def my_callback(sender, **kwargs):
    obj = kwargs['instance']
    if not obj.id and not obj.username:
       username = get_unique_username(obj.first_name, obj.last_name) # method that combines first name and last name then query on User model, if record found, will append integer 1 and then query again, until found unique username
       obj.username = username
pre_save.connect(my_callback, sender=User)
