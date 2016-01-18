from django.shortcuts import render
from .forms import ParticipationForm
from .models import Member, Transaction
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone

class ParticipationView(FormView):
    template_name = 'danceclub/participate.html'
    form_class = ParticipationForm
    success_url = '/dc/participate'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save(True)
        return super().form_valid(form)
        
class MemberView(TemplateView):
    template_name = 'danceclub/member.html'
    
    def get_context_data(self, member_id, member_name):
        ctx = super().get_context_data()
        member = get_object_or_404(Member, id=member_id, user__last_name__iexact=member_name)
        ctx["member"] = member
        transactions = Transaction.objects.filter(owner=member)
        saldo = transactions.aggregate(Sum('amount'))['amount__sum']
        ctx["transactions"] = transactions
        ctx["saldo"] = saldo
        if saldo and member.reference_numbers:
            barcode = "4"
            barcode = barcode + "6556121120318099"
            intpart,decimalpart = int(saldo),int((saldo-int(saldo))*100)
            barcode = barcode + str(1000000 - intpart)[1:]
            barcode = barcode + str(100 - decimalpart)[1:]
            barcode = barcode + '000'
            barcode = barcode + str(member.reference_numbers.first().number).zfill(20)
            barcode = barcode + timezone.now().strftime("%Y%m%d")
            ctx['barcode'] = barcode
        return ctx