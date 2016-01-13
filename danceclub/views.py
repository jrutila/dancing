from django.shortcuts import render
from .forms import ParticipationForm
from django.views.generic.edit import FormView

class ParticipationView(FormView):
    template_name = 'danceclub/participate.html'
    form_class = ParticipationForm
    success_url = '/dc/participate'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save(True)
        return super().form_valid(form)