"""
URL configuration for pawpark project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pawpark import error_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("parks.urls")),
    path("profiles/", include("profiles.urls")),
    path("accounts/", include("accounts.urls")),
    path("test400/", error_views.trigger_400),
    path("test403/", error_views.trigger_403),
    path("test404/", error_views.trigger_404),
    path("test500/", error_views.trigger_500),
    path("announcements/", include("announcements.urls")),
    path("moderation/", include("moderation.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
