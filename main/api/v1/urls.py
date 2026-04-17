"""URL configuration for the resource manager API."""

from django.urls import path

from .views import (
    add_resource,
    query_resource,
    release_resource,
    remove_resource,
    request_resource,
)

urlpatterns = [
    path("add_resource/", add_resource, name="add_resource"),
    path("remove_resource/", remove_resource, name="remove_resource"),
    path("query_resource/", query_resource, name="query_resource"),
    path("request_resource/", request_resource, name="request_resource"),
    path("release_resource/", release_resource, name="release_resource"),
]
