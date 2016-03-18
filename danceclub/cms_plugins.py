from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from .models import DanceEvent
from django.utils import timezone

class PossibleEventsPlugin(CMSPluginBase):
    model = CMSPlugin
    render_template = "danceclub/possible_events.html"
    name = _("Possible Events")
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']
        context['instance'] = instance
        context['events'] = events = DanceEvent.objects.filter(end__gte=timezone.now()).order_by('start')
        return context

plugin_pool.register_plugin(PossibleEventsPlugin)
