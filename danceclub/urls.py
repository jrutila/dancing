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
from .views import ParticipationView, MemberView, CancelView, LostLinkView, MassTransactionView, DanceEventsView
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    #url(r'$', redirect('participate')),
    url(r'$', ParticipationView.as_view(), name='participate'),
    url(r'info/(?P<member_id>[^/]+)/(?P<member_name>\w+)/$', MemberView.as_view(), name='member_info'),
    url(r'cancel/$', CancelView.as_view(), name='cancel'),
    url(r'lostlink/$', LostLinkView.as_view(), name='lost-link'),
    
    # Dancer restricted urls
    url(r'dance/events$', DanceEventsView.as_view(), name='dance_events'),

    # Admin urls
    url(r'upload/$', staff_member_required(MassTransactionView.as_view()), name='upload-transaction'),
]