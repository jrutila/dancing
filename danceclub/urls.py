"""danceclub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import ParticipationView, MemberView, CancelView, LostLinkView, MassTransactionView, DanceEventsView, DanceEventParticipationView
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from danceclub.views import CompetitionListClassesView, CompetitionListClubsView
from danceclub.views import competition_tps7_view

app_name = 'danceclub'
urlpatterns = [
    #url(r'$', redirect('participate')),
    url(r'$', ParticipationView.as_view(), name='participate'),
    url(r'(?P<event_id>\d+)$', DanceEventParticipationView.as_view(), name='dance_participate'),
    url(r'info/(?P<member_id>[^/]+)/$', MemberView.as_view(), name='member_info'),
    url(r'cancel/$', CancelView.as_view(), name='cancel'),
    url(r'lostlink/$', LostLinkView.as_view(), name='lost-link'),
    
    # Dancer restricted urls
    url(r'dance/events$', DanceEventsView.as_view(), name='dance_events'),
    
    # Admin urls
    url(r'upload/$', staff_member_required(MassTransactionView.as_view()), name='upload-transaction'),
]