from django.db.models.signals import post_save, post_delete
from django.core.signals import request_finished
from django.dispatch import receiver
from ..models import Member
from ..models import ReferenceNumber
from ..models import ActivityParticipation, Season, Transaction, Activity
from django.contrib.contenttypes.models import ContentType
from ..models import season_cost
from decimal import Decimal

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Member)
def create_refnumber(instance, created, **kwargs):
    logger.debug("post_save %s" % instance.user.first_name)
    if not instance.reference_numbers.count():
        ReferenceNumber.objects.create(
            object=instance)
            
@receiver(post_save, sender=ActivityParticipation)
@receiver(post_delete, sender=ActivityParticipation)
def set_activity_transactions(instance, **kwargs):
    season = Season.objects.get_season(instance.activity)
    owner = instance.member
    acts = ActivityParticipation.objects.filter(
        member=instance.member,
        activity__start__gte=season.start,
        activity__end__lte=season.end).order_by('-activity__type')
    Transaction.objects.filter(
        owner=instance.member,
        source_type=ContentType.objects.get_for_model(Activity),
        source_id=instance.activity.id
    ).delete()
    
    if 'created' in kwargs:
        Transaction.objects.get_or_create(
            source_type=ContentType.objects.get_for_model(season),
            source_id=season.id,
            owner=owner,
            defaults={
            'amount':-1*season_cost,
            'created_at':instance.created_at,
            'title':"Jäsenmaksu %s" % str(season)
            })
        Transaction.objects.create(
            source=instance.activity,
            owner=instance.member,
            amount = Decimal('0.00'),
            created_at = instance.created_at,
            title = "%s (%s)" % (instance.activity.name, str(season)))
        
    if len(acts) == 0 and not 'created' in kwargs:
        # If all deleted
        Transaction.objects.filter(
            owner=instance.member,
            source_type=ContentType.objects.get_for_model(season),
            source_id=season.id).delete()
    else:
        trans = Transaction.objects.filter(
            owner=instance.member,
            source_type=ContentType.objects.get_for_model(Activity),
            source_id__in=[x.activity.id for x in acts])
        ids = [x.activity.id for x in acts]
        trans = sorted(trans, key=lambda x: ids.index(x.source.id))
        
        i = 0
            
        for t in trans:
            cost = { t.source.type: [t.source.cost] }
            key = t.source.type
            if key not in cost:
                key = '*'
            t.amount = -1*cost[key][i]
            if i < len(cost):
                i = i + 1;
            t.save()
