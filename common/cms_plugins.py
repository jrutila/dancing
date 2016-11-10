from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from common.models import HomeSlide, Activity
from django.utils.translation import ugettext_lazy as _
from cmsplugin_filer_image.cms_plugins import FilerImagePlugin
from cmsplugin_filer_image.models import ThumbnailOption

class SlidePlugin(CMSPluginBase):
    model = HomeSlide
    render_template = "home_slide.html"
    name = _("Homepage slide")
    cache = False

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context


plugin_pool.register_plugin(SlidePlugin)


class ActivityPlugin(CMSPluginBase):
    model = Activity
    render_template = "activity.html"
    name = _("Sport Activity")
    cache = False
    
    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context
        
plugin_pool.register_plugin(ActivityPlugin)

class SponsorPlugin(FilerImagePlugin):
    name = "Sponsori"

    def render(self, context, instance, placeholder):
        # causes to render with sponsor.html
        instance.style = "sponsor"
        return super().render(context, instance, placeholder)

plugin_pool.register_plugin(SponsorPlugin)