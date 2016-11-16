from django import template
from danceclub.models import OwnCompetition
from django.utils import timezone

register = template.Library()

class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name
    def render(self, context):
        context[self.var_name] = self.new_val
        return ''

@register.tag
def own_competition(parser, token):
    own = OwnCompetition.objects.filter(date__gte=timezone.now())[0]
    return SetVarNode(own, "own")
    
@register.filter
def agesort(als):
    return sorted(als)
    
@register.filter
def agelevel(al):
    choices = OwnCompetition._meta.get_field('agelevels').choices
    return [x[1] for x in choices if x[0] == al][0]
    
@register.filter
def extra_space(ll):
    ll = len(ll)
    if ll < 7:
        return range(0, 7-ll if ll > 5 else 2)
    elif ll == 7:
        return range(0,0)
    elif ll < 13:
        return range(0, 13-ll if ll > 10 else 2)
    elif ll == 13:
        return range(0,0)
    return range(0, 2)