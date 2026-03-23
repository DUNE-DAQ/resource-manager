from django.urls import path

from .views import add_resource, query_resource, take_resource, release_resource, index

urlpatterns = [
    path("", index, name="index"),
    path("add_resource/", add_resource, name="add_resource"),
    path("query_resource/", query_resource, name="query_resource"),
    path("take_resource/", take_resource, name="take_resource"),
    path("release_resource/", release_resource, name="release_resource"),
]
