# """
# URL configuration for pawpark project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/4.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path, include
# from homepage.views import health_check
# from homepage.views import test_db_connection
# from django.contrib.auth import views as auth_views
# from django.contrib import admin
# from django.urls import path, include
# from django.contrib.auth import views as auth_views
# from homepage.views import health_check, test_db_connection

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('parks/', include('parks.urls')),
#     path('', include('homepage.urls')),
#     path("health/", health_check),
#     path("dbtest/", test_db_connection),
#     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
# ]

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from homepage.views import health_check, test_db_connection, role_selection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('parks/', include('parks.urls')),
    path('', include('homepage.urls')),
    path('health/', health_check),
    path('dbtest/', test_db_connection),

    # Role selection page (new)
    path('select/', role_selection, name='role_selection'),

    # Login/Logout routes
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
