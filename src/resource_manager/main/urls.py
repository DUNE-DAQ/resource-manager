"""URL configuration for the main resource manager app."""

from django.urls import path

from .views import index

urlpatterns = [
    path("", index, name="index"),
]
