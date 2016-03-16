# Use datetime if not localizing timezones
import datetime
# Otherwise use timezone
from django.utils import timezone 

from django import template

register = template.Library()

@register.filter
def hours_ago(time, hours):
    return time + datetime.timedelta(hours=hours) < timezone.now()