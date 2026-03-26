"""URL configuration for resource_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

API_VERSION = "v1"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("main.urls")),
    path("api/", include(f"main.urls_api_{API_VERSION}")),
    path(f"api/{API_VERSION}/", include(f"main.urls_api_{API_VERSION}")),
]
