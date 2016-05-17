import csv

from decimal import Decimal

# For reversion 1.10 from reversion import revisions as reversion
import reversion
from django.contrib import messages
from io import TextIOWrapper

import re

from django.shortcuts import render
from .forms import ParticipationForm, CancelForm, LostLinkForm, MassTransactionForm, DanceEventParticipationForm
from .models import Member, Transaction, ReferenceNumber, ActivityParticipation, Season, AlreadyExists, DanceEvent, Dancer, Couple, DanceEventParticipation
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max, Q
from django.utils import timezone
import django_settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
import datetime
from django.core.mail import send_mail
from django.http import Http404

from functools import wraps
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

def get_member_url(member):
    return reverse('member_info', kwargs={
        'member_id': member.token
        })
        
def send_payment_email(request, member):
    send_mail(
        'Maksutietosi Dancingille',
        'Hei,\nkiitos osallistumisestasi.\nTarkista maksutietosi osoitteesta: %s\n\nTerveisin,\nTanssiklubi Dancing' % request.build_absolute_uri(get_member_url(member)),
        'sihteeri@dancing.fi',
        [member.user.email], fail_silently=False)
    
class DanceEventsView(TemplateView):
    template_name = 'danceclub/dance_events.html'
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        events = DanceEvent.objects.filter(
            end__gte=timezone.now()
            ).order_by('start')
        ctx['events'] = events
        ctx['dancer'] = None
        ctx['couple'] = None
        ctx['myp'] = []
        ctx['mye'] = []
        if self.request.user.is_authenticated():
            try:
                ctx['dancer'] = dancer = Dancer.objects.get(user=self.request.user)
                ctx['couple'] = couple = Couple.objects.filter(Q(man=dancer) | Q(woman=dancer)).filter(ended__isnull=True).first()
                for e in events:
                    setattr(e, 'possible', [couple.man, couple.woman])
                    if e.deadline and e.deadline < timezone.now():
                        e.possible = []
                    for p in e.participations.all():
                        if p.member.id in [c.id for c in couple]:
                            ctx['mye'].append(e.id)
                            ctx['myp'].append(p.id)
                            e.possible = [c for c in e.possible if c.id != p.member.id]
                        elif not e.cost_per_participant:
                            e.possible = []
            except Dancer.DoesNotExist:
                pass
        return ctx
        
class DanceEventParticipationView(FormView):
    template_name = 'danceclub/outsider.html'
    
    def dispatch(self, *args, **kwargs):
        self.event_id = kwargs['event_id']
        self.event = get_object_or_404(DanceEvent, id=self.event_id)
        if self.event.start <= timezone.now():
            raise Http404()
        if self.request.user.is_authenticated():
            pass
        elif 'lastpart' in self.request.session and self.request.session['lastpart'] == self.event.id:
            pass
        elif self.event.public_since == None or self.event.public_since > timezone.now():
            raise Http404()
        elif self.event.participations.count():
            raise Http404()
        return super().dispatch(*args, **kwargs)
        
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['event'] = self.event
        return ctx
        
    def get_form(self, *args, **kwargs):
        form = DanceEventParticipationForm(self.request.user, self.event, **self.get_form_kwargs())
        if 'participant' in form.fields and 'cancel' in form.fields:
            # Logged in user
            if form.fields['participant'].choices == [] and form.fields['cancel'].choices == []:
                return None
        elif self.event.participations.count():
            return None
        return form
        
    def form_valid(self, form):
        parts, created = form.update_parts()
        self.created = created
        if not self.request.user.is_authenticated():
            self.member = parts[0].member
            self.request.session['lastpart'] = self.event.id
            try:
                send_payment_email(self.request, self.member)
                self.mail_sent = True
                messages.add_message(self.request, messages.SUCCESS, 'Maksutiedot lähetetty osoitteeseen %s' % self.member.user.email)
            except smtplib.SMTPException:
                messages.add_message(self.request, messages.ERROR, 'Sähköpostin lähetys epäonnistui!')
        return super().form_valid(form)
        
    def get_success_url(self):
        if self.created:
            # Message not sent to email or this is a new user
            return get_member_url(self.member)
        if self.request.user.is_authenticated():
            return reverse('dance_events')
        return reverse('dance_participate', kwargs={'event_id': self.event.id})

class ParticipationView(FormView):
    template_name = 'danceclub/participate.html'
    form_class = ParticipationForm
    
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            dancer = Dancer.objects.filter(user=self.request.user)
            if dancer and 'no_redirect' not in self.request.GET:
                return HttpResponseRedirect(reverse('dance_events'))
        return super().dispatch(*args, **kwargs)
        
    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated():
            initial['first_name'] = self.request.user.first_name
            initial['last_name'] = self.request.user.last_name
            initial['email'] = self.request.user.email
        return initial

    @reversion.create_revision()
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        m,created = form.save(True)
        self.member = form.member
        self.created = created
        self.mail_sent = False
        if self.member.user.email:
            try:
                send_payment_email(self.request, self.member)
                self.mail_sent = True
                messages.add_message(self.request, messages.SUCCESS, 'Maksutiedot lähetetty osoitteeseen %s' % self.member.user.email)
            except smtplib.SMTPException:
                messages.add_message(self.request, messages.ERROR, 'Sähköpostin lähetys epäonnistui!')
        return super().form_valid(form)
        
    def get_success_url(self):
        if not self.mail_sent or self.created:
            # Message not sent to email or this is a new user
            return get_member_url(self.member)
        return reverse('participate')
            
class CancelView(FormView):
    form_class = CancelForm

    @reversion.create_revision()
    def form_valid(self, form):
        self.member = Member.objects.get(token=form.cleaned_data['member'])
        actpart = ActivityParticipation.objects.filter_canceable(self.member).get(id=form.cleaned_data['actpartid'])
        actpart.delete()
        return super().form_valid(form)
        
    def get_success_url(self):
        return get_member_url(self.member)
            
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
    
    def get_context_data(self, member_id):
        ctx = super().get_context_data()
        member = get_object_or_404(Member, token=member_id)
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
        
class MassTransactionView(FormView):
    template_name = "danceclub/generic_form.html"
    form_class = MassTransactionForm

    def get_success_url(self):
        return reverse('upload-transaction')

    def form_valid(self, form):
        file = TextIOWrapper(self.request.FILES['file'].file, encoding='ascii', errors='replace')
        reader = csv.reader(file, delimiter=';')
        transactions = []
        for row in reader:
            tr = {}
            if row == []:
                continue
            try:
                tr['created_at'] = datetime.datetime.strptime(row[0], '%d.%m.%Y')
            except ValueError:
                continue
            tr['amount'] = Decimal(row[2].replace(',','.'))
            if tr['amount'] <= 0:
                continue
            tr['title'] = row[4] + " " + row[5]
            if 'ref' not in tr or tr['ref'] == '':
                messages.add_message(self.request, messages.ERROR, 'Empty reference number: ' + str(tr) )
                continue
            tr['ref'] = int(row[7])
            transactions.append(tr)
            #messages.add_message(self.request, messages.SUCCESS, row)
        succeeded = len(transactions)
        for tr in transactions:
            try:
                tr = Transaction.objects.add_transaction(**tr)
            except ReferenceNumber.DoesNotExist:
                messages.add_message(self.request, messages.ERROR, 'No such reference number %s' % tr['source'])
                succeeded = succeeded - 1
                continue
            except AlreadyExists:
                succeeded = succeeded - 1
                continue

            messages.add_message(self.request, messages.SUCCESS, tr)
        messages.add_message(self.request, messages.SUCCESS, '%d transactions uploaded!' % succeeded)

        return super().form_valid(form)
