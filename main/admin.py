"""Admin configuration for the main resource manager app."""

from django.contrib import admin

from .models import Resource

admin.site.register(Resource)
