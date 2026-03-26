"""Models for the main resource manager app."""

from django.db import models


class Resource(models.Model):
    """Model for a manageable resource."""

    name = models.CharField(primary_key=True, max_length=200)
    owner = models.CharField(max_length=200, null=True)
