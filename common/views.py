from django.shortcuts import render
from django.views.generic.base import RedirectView
from danceclub.views import get_member_url
from django.core.urlresolvers import reverse
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
        try:
            member = Member.objects.get(user=self.request.user)
        except Member.DoesNotExist:
            # No member, just a user
            if self.request.user.has_perm("danceclub.view_danceeventparticipation"):
                return reverse("dance_events")
            else:
                return "/"
        return get_member_url(member)