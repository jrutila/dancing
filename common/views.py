from django.shortcuts import render
from django.views.generic.base import RedirectView
from danceclub.views import get_member_url
from danceclub.models import Member
from django.contrib.auth.decorators import login_required

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

class ProfileRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    def get_redirect_url(self, *args, **kwargs):
        member = Member.objects.get(user=self.request.user)
        return get_member_url(member)