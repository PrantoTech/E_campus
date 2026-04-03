"""
URL configuration for E_campus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from E_campus import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/logout/', views.admin_logout_redirect, name='admin_logout_redirect'),
    path('admin/', admin.site.urls),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('image_gallery/', views.image_gallery, name='image_gallery'),
    path('students/', include('apps.students.urls')),
    path('faculty/', include('apps.faculty.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
