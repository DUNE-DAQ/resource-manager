"""Models for the main resource manager app."""

from django.db import models


class Resource(models.Model):
    """Model for a manageable resource."""

    name = models.CharField(primary_key=True, max_length=200)
    session_id = models.CharField(max_length=200, null=True)
    session_name = models.CharField(max_length=200, null=True)
    user_name = models.CharField(max_length=200, null=True)
