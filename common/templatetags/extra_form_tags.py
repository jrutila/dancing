from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name="list")
def to_list(value):
    return list(value)
    
@register.filter()
def get_field(value, arg):
    return value[arg]