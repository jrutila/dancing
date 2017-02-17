import csv

from decimal import Decimal

# For reversion 1.10 from reversion import revisions as reversion
import reversion
from django.contrib import messages
from io import TextIOWrapper

import re

from django.shortcuts import render
from .forms import ParticipationForm, CancelForm, LostLinkForm, MassTransactionForm, DanceEventParticipationForm
from .forms import couples
from .models import Member, Transaction, ReferenceNumber, ActivityParticipation, Season, AlreadyExists, DanceEvent, Dancer, Couple, DanceEventParticipation
from .models import OwnCompetition, CompetitionParticipation
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Max, Q, Count
from django.utils import timezone
from django.shortcuts import redirect
import django_settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
import datetime
from django.core.mail import send_mail
from django.http import Http404
import re

from functools import wraps
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from .models import Activity

def get_member_url(member):
    return reverse('member_info', kwargs={
        'member_id': member.token
        })
        
def send_payment_email(request, member, message):
    message = message or 'Hei,\nkiitos osallistumisestasi.\nTarkista maksutietosi osoitteesta: %s\n\nTerveisin,\nTanssiklubi Dancing'
    send_mail(
        'Maksutietosi Dancingille',
        message % request.build_absolute_uri(get_member_url(member)),
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
                # If not dancer but can see participations
                if self.request.user.has_perm("danceclub.view_danceeventparticipation"):
                    for e in events:
                        if e.participations.count():
                            ctx['mye'].append(e.id)
        return ctx
        
class DanceEventParticipationView(FormView):
    template_name = 'danceclub/outsider.html'
    
    def dispatch(self, *args, **kwargs):
        self.event_id = kwargs['event_id']
        self.event = get_object_or_404(DanceEvent, id=self.event_id)
        if self.request.user.is_authenticated():
            return super().dispatch(*args, **kwargs)
        if self.event.start <= timezone.now():
            raise Http404()
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
        # Group events can be attended always
        if self.event.cost_per_participant:
            return form
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
        if parts:
            self.member = parts[0].member
            self.request.session['lastpart'] = self.event.id
            try:
                send_payment_email(self.request, self.member)
                self.mail_sent = True
                messages.add_message(self.request, messages.SUCCESS, 'Maksutiedot lähetetty osoitteeseen %s' % self.member.user.email)
            except smtplib.SMTPException:
                messages.add_message(self.request, messages.ERROR, 'Sähköpostin lähetys epäonnistui!')
        else:
            self.member = None
        return super().form_valid(form)
        
    def get_success_url(self):
        if self.created and self.member:
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
            if dancer or self.request.user.has_perm("danceclub.view_danceeventparticipation"):
                if 'no_redirect' not in self.request.GET:
                    return HttpResponseRedirect(reverse('dance_events'))
        return super().dispatch(*args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['season'] = Season.objects.current_or_next_season()
        context['disabled'] = Activity.objects.filter(season=context['season'],active=False)
        return context
        
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
            message = None
            for act in form.cleaned_data['activities']:
                message = act.mail_message or None
            try:
                send_payment_email(self.request, self.member, message)
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
        members = Member.objects.filter(user__email=form.cleaned_data['email'])
        if not members.count():
            self.failed = "Antamaasi sähköpostiosoitetta ei löytynyt"
            return super().form_valid(form)
        
        
        self.lostlink = "Maksutietolinkki lähetetty osoitteeseen "+form.cleaned_data['email']
        links = ""
        for m in members:
            links = links + "\t%s - %s\n" % (m, self.request.build_absolute_uri(get_member_url(m)))
        send_mail(
            'Maksutietosi Dancingille',
            'Hei,\nTarkista maksutietosi osoitteesta:\n%s\n\nTerveisin,\nTanssiklubi Dancing' % links,
            'sihteeri@dancing.fi',
            [form.cleaned_data['email']], fail_silently=False)
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
        # Limit transactions to only show the latest
        ctx["transactions"] = []
        sld = 0
        if saldo != None and saldo < 0:
            for tr in list(transactions.order_by('created_at')):
                sld = sld + tr.amount
                if sld >= Decimal('0.00'):
                    ctx["transactions"] = []
                if sld != Decimal('0.00'):
                    ctx["transactions"].append(tr)
        else:
            season_type = ContentType.objects.get_for_model(ctx["season"])
            act_type = ContentType.objects.get_for_model(Activity)
            acts = Activity.objects.filter(
                season=ctx["season"]
            ).values_list('id', flat=True)
            ctx["transactions"] = transactions.filter(
                Q(source_type=season_type.id, source_id=ctx["season"].id) |
                Q(source_type=act_type.id, source_id__in=acts))

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
            tr['amount'] = Decimal(row[4].replace(',','.'))
            if tr['amount'] <= 0:
                continue
            tr['title'] = row[2]
            reff = re.sub('[^0-9]', '', row[3])
            if reff:
                tr['ref'] = int(reff)
            if 'ref' not in tr or tr['ref'] == '':
                messages.add_message(self.request, messages.ERROR, 'Empty reference number: ' + str(tr) )
                continue
            transactions.append(tr)
            #messages.add_message(self.request, messages.SUCCESS, row)
        succeeded = len(transactions)
        for tr in transactions:
            try:
                tra = Transaction.objects.add_transaction(**tr)
                setattr(tra, 'ref', tr['ref'])
            except ReferenceNumber.DoesNotExist:
                messages.add_message(self.request, messages.ERROR, 'No such reference number %s' % tr)
                succeeded = succeeded - 1
                continue
            except AlreadyExists:
                messages.add_message(self.request, messages.INFO, "Already exists: %s" % tr)
                succeeded = succeeded - 1
                continue

            messages.add_message(self.request, messages.SUCCESS, tra)
        messages.add_message(self.request, messages.SUCCESS, '%d transactions uploaded!' % succeeded)

        return super().form_valid(form)
        
class CompetitionIndex(TemplateView):
    template_name = 'danceclub/competition_index.html'
    
    def dispatch(self, request, *args, **kwargs):
        curr = OwnCompetition.objects.get(date__gte=timezone.now())
        if curr:
            return redirect(curr.get_absolute_url())
    
        return super().dispatch(request, *args, **kwargs)

class CompetitionView(TemplateView):
    template_name = 'danceclub/competition.html'
    
    def get_context_data(self, slug):
        ctx = super().get_context_data()
        competition = get_object_or_404(OwnCompetition, slug=slug)
        ctx["competition"] = competition
        ctx["now"] = timezone.now();
        ctx["show_info"] = competition.deadline < ctx["now"]
        if ctx["show_info"]:
            ctx["participations"] = dict([(x,[c for c in competition.participations.all() if c.level == x]) for x in competition.agelevels])
        counts = competition.participations.values("level").annotate(amount=Count("competition"))
        counts = dict([ (c["level"], c["amount"]) for c in counts])
        for al in competition.agelevels:
            if not al in counts:
                counts[al] = 0
        ctx["counts"] = counts
        return ctx
        
from django.forms import formset_factory, BaseFormSet
from .forms import CompetitionEnrollForm, CompetitionEnrollPairForm
from django.utils import formats
from django.utils.functional import cached_property

class CompetitionEnrollFormSet(BaseFormSet):
    @cached_property
    def forms(self):
        """
        Instantiate forms at first property access.
        """
        # DoS protection is included in total_form_count()
        forms = [self._construct_form(i, competition=self.competition, club=self.club) for i in range(self.total_form_count())]
        return forms

class CompetitionEnrollView(FormView):
    template_name = "danceclub/competition_form.html"
    form_class = CompetitionEnrollForm
    
    def dispatch(self, request, *args, **kwargs):
        if 'club' in kwargs:
            self.club = int(kwargs['club'])
        else:
            self.club = None
        self.competition = get_object_or_404(OwnCompetition, slug=kwargs['slug'])
        
        if (self.competition.deadline < timezone.now() and not request.GET.get('secret', None)):
            raise Http404("Ilmoittautumisaika on päättynyt")
            
        self.formset = formset_factory(
            CompetitionEnrollPairForm,
            formset=CompetitionEnrollFormSet,
            extra=10)
        self.formset.competition = self.competition
        if self.club:
            field = self.form_class(self.competition).fields['club']
            choice = field.choices[self.club]
            self.formset.club = choice[0]
        #(competition = self.competition)
        return super(CompetitionEnrollView,self).dispatch(request, *args, **kwargs)
        
    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        if self.club:
            field = self.form_class(self.competition).fields['club']
            choice = field.choices[self.club]
            initial['club'] = choice[0]
        return initial
        
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args,**kwargs)
        ctx['formset'] = self.formset
        return ctx
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['competition'] = self.competition
        return kwargs
        
    def get_success_url(self):
        als = dict(OwnCompetition._meta.get_field('agelevels').choices)
        msg = '''
        <p>Seuraavat osallistujat rekisteröity:</p>
        <ul>
        '''
        for p in self.saved:
            msg = msg + "<li>%s - %s, %s</li>" % (p.man, p.woman, als[p.level])
        msg = msg + "</ul>"
        
        msg_email = ""
        for p in self.saved:
            msg_email = msg_email + "  %s - %s, %s\n" % (p.man, p.woman, als[p.level])
        email_succ = send_mail(
            'Ilmoittautuminen kisaan %s' % formats.date_format(self.competition.date, "SHORT_DATE_FORMAT"),
            'Hei,\nkiitos ilmoittautumisista.\nSeuraavat ilmoittautumiset rekisteröity:\n\n%s\n%s\n\nTervetuloa kisaamaan,\nTanssiklubi Dancing\nkilpailut@dancing.fi' % (self.club, msg_email),
            'kilpailut@dancing.fi',
            ["kilpailut@dancing.fi", self.enroll_email], fail_silently=True)
        if email_succ:
            msg = msg + "<p>Sähköpostiviesti lähetetty osoitteeseen: %s</p>" % self.enroll_email

        messages.add_message(self.request, messages.SUCCESS, msg)

        return self.competition.get_absolute_url()
        
    def form_valid(self, form):
        form.save()
        self.saved = form.parts
        self.enroll_email = form.cleaned_data['enroller_email']
        self.club = form.cleaned_data['club']
        return super().form_valid(form)

class CompetitionListClassesView(TemplateView):
    template_name = "danceclub/admin/competition_list_classes.html"
    
    def get_context_data(self):
        competition = OwnCompetition.objects.order_by('start')[0]
        participations = CompetitionParticipation.objects.filter(competition=competition).order_by('level','number')
        ctx = super().get_context_data()
        ctx['competition'] = competition
        ctx['participations'] = participations
        return ctx
        
import csv
from django.http import HttpResponse
from .models import age_code
def competition_tps7_view(request):
    split_names = request.GET.get('split_names', False)
    # Create the HttpResponse object with the appropriate CSV header.
    competition = OwnCompetition.objects.order_by('start')[0]
    participations = CompetitionParticipation.objects.filter(competition=competition).order_by('level','number')
    response = HttpResponse(content_type='text/cvs')
    response['Content-Disposition'] = 'attachment; filename="'+competition.slug+'.csv"'

    writer = csv.writer(response)
    for p in participations:
        if not split_names:
            writer.writerow([age_code(p.level), p.number, p.man, p.woman, p.club])
        else:
            writer.writerow([age_code(p.level), p.number] + p.man.split(" ") + p.woman.split(" ") + [p.club])

    return response

class CompetitionListClubsView(TemplateView):
    template_name = "danceclub/admin/competition_list_clubs.html"
    
    def get_context_data(self):
        competition = OwnCompetition.objects.order_by('start')[0]
        #try:
            #participations = list(CompetitionParticipation.objects.filter(competition=competition).order_by('club','number').distinct('man','woman','club'))
        #except NotImplementedError:
        
        seen = dict()
        participations = list(CompetitionParticipation.objects.filter(competition=competition).order_by('club','number'))
        parts = []
        for p in participations:
            if (p.man, p.woman, p.club) not in seen:
                seen[(p.man, p.woman, p.club)] = p
                setattr(p, 'levels', [p.level])
                parts.append(p)
            else:
                pp = seen[(p.man, p.woman, p.club)]
                pp.levels.append(p.level)
                pp.paid = pp.paid or p.paid
            
        ctx = super().get_context_data()
        ctx['competition'] = competition
        ctx['participations'] = parts
        return ctx