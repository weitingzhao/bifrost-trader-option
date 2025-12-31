"""Django URL configuration."""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # TODO: Add API URLs if using Django REST Framework
]

