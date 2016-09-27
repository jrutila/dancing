"""competition URL Configuration
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import CompetitionView, CompetitionEnrollView, CompetitionIndex
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    url(r'^$', CompetitionIndex.as_view(), name='competition_index'),
    url(r'(?P<slug>[^/]+)/$', CompetitionView.as_view(), name='competition_info'),
    url(r'(?P<slug>[^/]+)/enroll/$', CompetitionEnrollView.as_view(), name='competition_enroll'),
]