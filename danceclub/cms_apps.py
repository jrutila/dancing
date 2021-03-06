"""CMS apphook for the ``image_gallery`` app."""
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

class DanceClubApphook(CMSApp):
    name = _("Dance club app hook")
    urls = ["danceclub.urls"]
    app_name = "danceclub"
    
apphook_pool.register(DanceClubApphook)

class CompetitionAppHook(CMSApp):
    name = _("Competition app hook")
    urls = ["danceclub.competition_urls"]
    app_name = "danceclub_competition"
    
apphook_pool.register(CompetitionAppHook)