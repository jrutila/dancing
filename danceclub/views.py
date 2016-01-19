import re

from django.shortcuts import render
from .forms import ParticipationForm, CancelForm, LostLinkForm
from .models import Member, Transaction, ReferenceNumber, ActivityParticipation, Season
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max
from django.utils import timezone
import django_settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
import datetime
from django.core.mail import send_mail

def get_member_url(member):
    return reverse('member_info', kwargs={
        'member_id': member.id,
        'member_name': member.user.last_name
        })
    

class ParticipationView(FormView):
    template_name = 'danceclub/participate.html'
    form_class = ParticipationForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save(True)
        self.member = form.member
        if self.member.user.email:
            send_mail(
                'Maksutietosi Dancingille',
                'Hei,\nkiitos osallistumisestasi.\nTarkista maksutietosi osoitteesta: %s\n\nTerveisin,\nTanssiklubi Dancing' % self.request.build_absolute_uri(self.get_success_url()),
                'sihteeri@dancing.fi',
                [self.member.user.email], fail_silently=True)
        return super().form_valid(form)
        
    def get_success_url(self):
        return get_member_url(self.member)
            
class CancelView(FormView):
    form_class = CancelForm
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        self.member = Member.objects.get(token=form.cleaned_data['member'])
        actpart = ActivityParticipation.objects.filter_canceable(self.member).get(id=form.cleaned_data['actpartid'])
        actpart.delete()
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('member_info', kwargs={
            'member_id': self.member.id,
            'member_name': self.member.user.last_name
            })
            
class LostLinkView(FormView):
    form_class = LostLinkForm
    
    def form_valid(self, form):
        self.failed = None
        try:
            self.member = Member.objects.get(user__email=form.cleaned_data['email'])
        except Member.DoesNotExist:
            self.failed = "Antamaasi sähköpostiosoitetta ei löytynyt"
            return super().form_valid(form)
        
        self.lostlink = "Maksutietolinkki lähetetty osoitteeseen "+self.member.user.email
        send_mail(
            'Maksutietosi Dancingille',
            'Hei,\nTarkista maksutietosi osoitteesta: %s\n\nTerveisin,\nTanssiklubi Dancing' % self.request.build_absolute_uri(get_member_url(self.member)),
            'sihteeri@dancing.fi',
            [self.member.user.email], fail_silently=False)
        return super().form_valid(form)
        
    def get_success_url(self):
        if self.failed:
            return reverse('participate')+"?failed="+self.failed
        return reverse('participate')+"?lostlink="+self.lostlink
        
class MemberView(TemplateView):
    template_name = 'danceclub/member.html'
    
    def get_context_data(self, member_id, member_name):
        ctx = super().get_context_data()
        member = get_object_or_404(Member, id=member_id, user__last_name__iexact=member_name)
        ctx["season"] = Season.objects.current_season()
        ctx["member"] = member
        transactions = Transaction.objects.filter(owner=member)
        saldo = transactions.aggregate(Sum('amount'))['amount__sum']
        ctx["transactions"] = list(transactions.order_by('created_at'))
        ctx['acts'] = ActivityParticipation.objects.filter_canceable(member=member)
        for a in ctx['acts']:
            tr = [x for x in ctx['transactions'] if x.source == a.activity]
            if tr:
                tr[0].cancel = CancelForm({ 'actpartid': a.id, 'member': member.token })
        ctx["saldo"] = saldo
        ctx["last_check"] = Transaction.objects.filter(
            source_type=ContentType.objects.get_for_model(ReferenceNumber)).aggregate(
                Max('created_at'))['created_at__max']
        if saldo and member.reference_numbers:
            barcode = "4"
            barcode = barcode + re.sub(r"[A-Za-z\s]+", "", django_settings.get('bank_account'))
            intpart,decimalpart = int(saldo),int((saldo-int(saldo))*100)
            barcode = barcode + str(1000000 - intpart)[1:]
            barcode = barcode + str(100 - decimalpart)[1:]
            barcode = barcode + '000'
            barcode = barcode + str(member.reference_numbers.first().number).zfill(20)
            barcode = barcode + timezone.now().strftime("%Y%m%d")
            ctx['barcode'] = barcode
        return ctx