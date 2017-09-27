"""competition URL Configuration
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import CompetitionView, CompetitionEnrollView, CompetitionIndex, CompetitionEnrollClubSelectView
from .views import CompetitionListClassesView, CompetitionListClubsView, competition_tps7_view
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    url(r'^$', CompetitionIndex.as_view(), name='competition_index'),
    url(r'(?P<slug>[^/]+)/$', CompetitionView.as_view(), name='competition_info'),
    url(r'(?P<slug>[^/]+)/enroll/$', CompetitionEnrollClubSelectView.as_view(), name='competition_enroll'),
    url(r'(?P<slug>[^/]+)/enroll/(?P<club>.+)/$', CompetitionEnrollView.as_view(), name='competition_enroll'),

    # Reports
    url(r'(?P<slug>[^/]+)/listclasses/$', CompetitionListClassesView.as_view(), name='list-classes'),
    url(r'(?P<slug>[^/]+)/listclubs/$', CompetitionListClubsView.as_view(), name='list-clubs'),
    url(r'(?P<slug>[^/]+)/tps7/$', competition_tps7_view, name='list-tps7'),

]