from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from common.models import HomeSlide, Activity
from django.utils.translation import ugettext_lazy as _

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