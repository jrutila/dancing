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
def agelevel(al):
    return [x[1] for x in OwnCompetition._meta.get_field('agelevels').choices if x[0] == al][0]