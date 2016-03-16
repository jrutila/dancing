from django.shortcuts import render
from django.views.generic.base import RedirectView
from danceclub.views import get_member_url
from danceclub.models import Member

class ProfileRedirectView(RedirectView):
    permanent = False
    def get_redirect_url(self, *args, **kwargs):
        member = Member.objects.get(user=self.request.user)
        return get_member_url(member)