"""dancing URL Configuration

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
from common.views import ProfileRedirectView
from .forms import EmailAuthenticationForm
from django.contrib.auth.views import password_reset
from .forms import NonPasswordResetForm
from django.contrib.auth.views import login

urlpatterns = []
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += [
    url(r'^accounts/profile/', ProfileRedirectView.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/', include('loginas.urls')),
    url(r'^filer/', include('filer.urls')),
    #url(r'^password_reset/$', password_reset, {'password_reset_form': NonPasswordResetForm}, name='password_reset'),
    url(r'^password_reset/$', password_reset, {'password_reset_form': NonPasswordResetForm}, name='password_reset'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^', include('cms.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
