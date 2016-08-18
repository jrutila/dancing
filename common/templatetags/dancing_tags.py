# Use datetime if not localizing timezones
import datetime
# Otherwise use timezone
from django.utils import timezone 
from django.conf import settings

from django import template

from common.models import NameColor
import random

register = template.Library()

@register.filter
def hours_ago(time, hours):
    return time + datetime.timedelta(hours=hours) < timezone.now()

    
@register.filter
def to_color(name):
    col,cr = NameColor.objects.get_or_create(
        name = name
        )
    return col.color

class ShowGoogleAnalyticsJS(template.Node):
	def render(self, context):
		code =  getattr(settings, "GOOGLE_ANALYTICS_CODE", False)
		if not code:
			return "<!-- Goggle Analytics not included because you haven't set the settings.GOOGLE_ANALYTICS_CODE variable! -->"

		#if 'user' in context and context['user'] and context['user'].is_staff:
			#return "<!-- Goggle Analytics not included because you are a staff user! -->"

		if settings.DEBUG:
			return "<!-- Goggle Analytics not included because you are in Debug mode! -->"

		return """
		<script type="text/javascript">
			var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
			document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
		</script>
		<script type="text/javascript">
			try {
			var pageTracker = _gat._getTracker('""" + str(code) + """');
			pageTracker._trackPageview();
		} catch(err) {}</script>
		"""

@register.tag
def googleanalyticsjs(parser, token):
	return ShowGoogleAnalyticsJS()