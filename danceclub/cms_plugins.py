from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from .models import DanceEvent, Dancer
from django.utils import timezone
import datetime
from django.db.models import Count, Q, BooleanField, ExpressionWrapper

class PossibleEventsPlugin(CMSPluginBase):
    model = CMSPlugin
    render_template = "danceclub/possible_events.html"
    name = _("Possible Events")
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']
        context['instance'] = instance
        dancer_filter = public_filter = Q(public_since__lte=timezone.now())
        if request.user.is_authenticated():
            try:
                dancer = Dancer.objects.get(user=request.user)
                dancer_filter =  Q(start__lte=timezone.now()+datetime.timedelta(days=4)) | Q(public=True)
            except Dancer.DoesNotExist:
                pass
            
        context['events'] = events = DanceEvent.objects.annotate(
            part_count=Count('participations'),
            public=ExpressionWrapper(public_filter, output_field=BooleanField())
            ).filter(
            end__gte=timezone.now(),
            part_count=0
            ).filter(dancer_filter).order_by('start')
        return context

plugin_pool.register_plugin(PossibleEventsPlugin)