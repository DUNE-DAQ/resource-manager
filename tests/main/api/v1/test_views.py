"""Test the view functions for the resource manager API version 1."""

import json

import pytest
from django.test import RequestFactory

from main.api.v1.views import add_resource
from main.models import Resource


@pytest.mark.django_db
class TestAddResource:
    """Tests for the add_resource view function."""

    def test_rejects_non_post(self):
        """Test that non-POST requests are rejected."""
        request = RequestFactory().get("/add-resource/")

        response = add_resource(request)

        assert response.status_code == 400
        payload = json.loads(response.content)
        assert payload == {"message": "Only POST requests are allowed. Received 'GET'."}
        assert Resource.objects.count() == 0

    def test_requires_names_argument(self):
        """Test that the 'names' argument is required."""
        request = RequestFactory().post("/add-resource/", data={})

        response = add_resource(request)

        assert response.status_code == 400
        payload = json.loads(response.content)
        assert payload == {"message": "Missing required argument 'names'."}
        assert Resource.objects.count() == 0

    def test_adds_resources(self):
        """Test that resources are added to the database."""
        request = RequestFactory().post(
            "/add-resource/",
            data={"names": "alpha,beta,gamma"},
        )

        response = add_resource(request)

        assert response.status_code == 201
        payload = json.loads(response.content)
        assert payload["message"] == "3 resources added."
        assert payload["duplicated"] == []

        assert set(Resource.objects.values_list("name", flat=True)) == {
            "alpha",
            "beta",
            "gamma",
        }

    def test_skips_existing_duplicates(self):
        """Test that existing resources are skipped and reported as duplicates."""
        Resource.objects.create(name="beta")

        request = RequestFactory().post(
            "/add-resource/",
            data={"names": "alpha,beta,gamma"},
        )

        response = add_resource(request)

        assert response.status_code == 201
        payload = json.loads(response.content)

        assert payload["message"] == "2 resources added. 1 duplicate resources skipped."
        assert set(payload["duplicated"]) == {"beta"}

        assert set(Resource.objects.values_list("name", flat=True)) == {
            "alpha",
            "beta",
            "gamma",
        }
