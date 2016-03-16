# Use datetime if not localizing timezones
import datetime
# Otherwise use timezone
from django.utils import timezone 

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