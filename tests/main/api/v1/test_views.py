"""Test the view functions for the resource manager API version 1."""

import json

import pytest
from django.test import RequestFactory

from resource_manager.main.api.v1.views import (
    add_resource,
    query_resource,
    release_resource,
    remove_resource,
    request_resource,
)
from resource_manager.main.models import Resource


@pytest.mark.django_db
class TestAddResource:
    """Tests for the add_resource view function."""

    def test_rejects_non_post(self):
        """Test that non-POST requests are rejected."""
        request = RequestFactory().get("/add-resource/")

        response = add_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Only POST requests are allowed. Received 'GET'."}
        assert Resource.objects.count() == 0

    def test_requires_names_argument(self):
        """Test that the 'names' argument is required."""
        request = RequestFactory().post("/add-resource/", data={})

        response = add_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Missing required argument 'names'."}
        assert Resource.objects.count() == 0

    def test_adds_resources(self):
        """Test that resources are added to the database."""
        request = RequestFactory().post(
            "/add-resource/",
            data={"names": "alpha,beta,gamma"},
        )

        response = add_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 201
        assert payload["message"] == "3 resources added."
        assert set(payload["added"]) == {"alpha", "beta", "gamma"}
        assert set(payload["duplicate"]) == set()
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
        payload = json.loads(response.content)

        assert response.status_code == 201
        assert payload["message"] == "2 resources added. 1 duplicate resources skipped."
        assert set(payload["added"]) == {"alpha", "gamma"}
        assert set(payload["duplicate"]) == {"beta"}
        assert set(Resource.objects.values_list("name", flat=True)) == {
            "alpha",
            "beta",
            "gamma",
        }


@pytest.mark.django_db
class TestRemoveResource:
    """Tests for the remove_resource view function."""

    def test_rejects_non_post(self):
        """Test that non-POST requests are rejected."""
        request = RequestFactory().get("/remove-resource/")

        response = remove_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Only POST requests are allowed. Received 'GET'."}
        assert Resource.objects.count() == 0

    def test_requires_names_argument(self):
        """Test that the 'names' argument is required."""
        request = RequestFactory().post("/remove-resource/", data={})

        response = remove_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Missing required argument 'names'."}
        assert Resource.objects.count() == 0

    def test_removes_unowned_resources(self):
        """Test that unowned resources are removed from the database."""
        Resource.objects.create(name="alpha")
        Resource.objects.create(name="beta")
        Resource.objects.create(name="gamma")

        request = RequestFactory().post(
            "/remove-resource/",
            data={"names": "alpha,beta,gamma"},
        )

        response = remove_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "3 resources removed."
        assert set(payload["removed"]) == {"alpha", "beta", "gamma"}
        assert set(payload["missing"]) == set()
        assert set(payload["already_owned"]) == set()
        assert Resource.objects.count() == 0

    def test_skips_missing_resources(self):
        """Test that missing resources are skipped and reported as missing."""
        Resource.objects.create(name="alpha")

        request = RequestFactory().post(
            "/remove-resource/",
            data={"names": "alpha,beta"},
        )

        response = remove_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "1 resources removed. 1 missing resources skipped."
        assert set(payload["removed"]) == {"alpha"}
        assert set(payload["missing"]) == {"beta"}
        assert set(payload["already_owned"]) == set()

    def test_skips_owned_resources(self):
        """Test that owned resources are skipped and reported as already-owned."""
        Resource.objects.create(name="alpha", owner="batman")
        Resource.objects.create(name="beta")

        request = RequestFactory().post(
            "/remove-resource/",
            data={"names": "alpha,beta"},
        )

        response = remove_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "1 resources removed. 1 already-owned resources skipped."
        assert set(payload["removed"]) == {"beta"}
        assert set(payload["missing"]) == set()
        assert set(payload["already_owned"]) == {"alpha"}
        assert Resource.objects.filter(name="alpha", owner="batman").exists()
        assert not Resource.objects.filter(name="beta").exists()


@pytest.mark.django_db
class TestQueryResource:
    """Tests for the query_resource view function."""

    def test_rejects_non_post(self):
        """Test that non-POST requests are rejected."""
        request = RequestFactory().get("/query-resource/")

        response = query_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Only POST requests are allowed. Received 'GET'."}
        assert Resource.objects.count() == 0

    def test_requires_names_argument(self):
        """Test that the 'names' argument is required."""
        request = RequestFactory().post("/query-resource/", data={})

        response = query_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Missing required argument 'names'."}
        assert Resource.objects.count() == 0

    def test_queries_existing_resources(self):
        """Test that existing resources are queried and returned in the response."""
        Resource.objects.create(
            name="alpha",
            owner="batman",
            session_id=None,
            session_name=None,
        )
        Resource.objects.create(
            name="beta",
            owner="alice",
            session_id="s2",
            session_name="session two",
        )

        request = RequestFactory().post(
            "/query-resource/",
            data={"names": "alpha,beta"},
        )

        response = query_resource(request)
        payload = json.loads(response.content)
        results_by_name = {r["name"]: r for r in payload["query_results"]}

        assert response.status_code == 200
        assert payload["message"] == "2 resources queried."
        assert set(payload["missing"]) == set()
        assert results_by_name == {
            "alpha": {
                "name": "alpha",
                "owner": "batman",
                "session_id": None,
                "session_name": None,
            },
            "beta": {
                "name": "beta",
                "owner": "alice",
                "session_id": "s2",
                "session_name": "session two",
            },
        }

    def test_skips_missing_resources(self):
        """Test that missing resources are skipped and reported as missing."""
        Resource.objects.create(name="alpha")

        request = RequestFactory().post(
            "/query-resource/",
            data={"names": "alpha,beta"},
        )

        response = query_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "1 resources queried. 1 missing resources skipped."
        assert set(payload["missing"]) == {"beta"}


@pytest.mark.django_db
class TestRequestResource:
    """Tests for the request_resource view function."""

    def test_rejects_non_post(self):
        """Test that non-POST requests are rejected."""
        request = RequestFactory().get("/request-resource/")

        response = request_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Only POST requests are allowed. Received 'GET'."}
        assert Resource.objects.count() == 0

    def test_requires_all_arguments(self):
        """Test that all arguments are required."""
        args = ["names", "owner", "session_id", "session_name"]
        data = {
            "names": "alpha",
            "owner": "batman",
            "session_id": "s1",
            "session_name": "session one",
        }

        for missing_arg in args:
            test_data = {k: v for k, v in data.items() if k != missing_arg}

            request = RequestFactory().post(
                "/request-resource/",
                data=test_data,
            )

            response = request_resource(request)
            payload = json.loads(response.content)

            assert response.status_code == 400
            assert payload == {"message": f"Missing required argument '{missing_arg}'."}
            assert Resource.objects.count() == 0

    def test_takes_unowned_resources(self):
        """Test that unowned resources are taken."""
        Resource.objects.create(name="alpha")
        Resource.objects.create(name="beta")

        request = RequestFactory().post(
            "/request-resource/",
            data={
                "names": "alpha,beta",
                "owner": "batman",
                "session_id": "s1",
                "session_name": "session one",
            },
        )

        response = request_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "2 resources taken."
        assert set(payload["taken"]) == {"alpha", "beta"}
        assert set(payload["missing"]) == set()
        assert set(payload["already_owned"]) == set()

        alpha = Resource.objects.get(name="alpha")
        assert alpha.owner == "batman"
        assert alpha.session_id == "s1"
        assert alpha.session_name == "session one"

        beta = Resource.objects.get(name="beta")
        assert beta.owner == "batman"
        assert beta.session_id == "s1"
        assert beta.session_name == "session one"

    def test_skips_missing_resources(self):
        """Test that missing resources are skipped and reported as missing."""
        Resource.objects.create(name="alpha")

        request = RequestFactory().post(
            "/request-resource/",
            data={
                "names": "alpha,beta",
                "owner": "batman",
                "session_id": "s1",
                "session_name": "session one",
            },
        )

        response = request_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "1 resources taken. 1 missing resources skipped."
        assert set(payload["taken"]) == {"alpha"}
        assert set(payload["missing"]) == {"beta"}
        assert set(payload["already_owned"]) == set()

    def test_fails_on_already_owned_resources(self):
        """Test that any already-owned resources cause a failure."""
        Resource.objects.create(
            name="alpha",
            owner="alice",
            session_id="old-sid",
            session_name="old session",
        )
        Resource.objects.create(name="beta")

        request = RequestFactory().post(
            "/request-resource/",
            data={
                "names": "alpha,beta",
                "owner": "batman",
                "session_id": "new-sid",
                "session_name": "new session",
            },
        )

        response = request_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload["message"] == "1 or more resources are already owned. Aborting."
        assert set(payload["taken"]) == set()
        assert set(payload["missing"]) == set()
        assert set(payload["already_owned"]) == {"alpha"}

        alpha = Resource.objects.get(name="alpha")
        assert alpha.owner == "alice"
        assert alpha.session_id == "old-sid"
        assert alpha.session_name == "old session"

        beta = Resource.objects.get(name="beta")
        assert beta.owner is None
        assert beta.session_id is None
        assert beta.session_name is None


@pytest.mark.django_db
class TestReleaseResource:
    """Tests for the release_resource view function."""

    def test_rejects_non_post(self):
        """Test that non-POST requests are rejected."""
        request = RequestFactory().get("/release-resource/")

        response = release_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 400
        assert payload == {"message": "Only POST requests are allowed. Received 'GET'."}
        assert Resource.objects.count() == 0

    def test_requires_all_arguments(self):
        """Test that all arguments are required."""
        args = ["names", "owner"]
        data = {
            "names": "alpha",
            "owner": "batman",
        }

        for missing_arg in args:
            test_data = {k: v for k, v in data.items() if k != missing_arg}

            request = RequestFactory().post(
                "/release-resource/",
                data=test_data,
            )

            response = release_resource(request)
            payload = json.loads(response.content)

            assert response.status_code == 400
            assert payload == {"message": f"Missing required argument '{missing_arg}'."}
            assert Resource.objects.count() == 0

    def test_releases_owned_resources(self):
        """Test that resources owned by the given owner are released."""
        Resource.objects.create(
            name="alpha",
            owner="batman",
            session_id="s1",
            session_name="session one",
        )
        Resource.objects.create(
            name="beta",
            owner="batman",
            session_id="s2",
            session_name="session two",
        )

        request = RequestFactory().post(
            "/release-resource/",
            data={
                "names": "alpha,beta",
                "owner": "batman",
            },
        )

        response = release_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "2 resources released."
        assert set(payload["missing"]) == set()
        assert set(payload["not_owned"]) == set()

        alpha = Resource.objects.get(name="alpha")
        assert alpha.owner is None
        assert alpha.session_id is None
        assert alpha.session_name is None

        beta = Resource.objects.get(name="beta")
        assert beta.owner is None
        assert beta.session_id is None
        assert beta.session_name is None

    def test_skips_missing_resources(self):
        """Test that missing resources are skipped and reported as missing."""
        Resource.objects.create(
            name="alpha",
            owner="batman",
            session_id="s1",
            session_name="session one",
        )

        request = RequestFactory().post(
            "/release-resource/",
            data={
                "names": "alpha,beta",
                "owner": "batman",
            },
        )

        response = release_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "1 resources released. 1 missing resources skipped."
        assert set(payload["missing"]) == {"beta"}
        assert set(payload["not_owned"]) == set()

    def test_skips_not_owned_resources(self):
        """Test that not-owned resources are skipped and reported as not-owned."""
        Resource.objects.create(
            name="alpha",
            owner="batman",
            session_id="s1",
            session_name="session one",
        )
        Resource.objects.create(
            name="beta",
            owner="alice",
            session_id="a1",
            session_name="alice_session",
        )
        Resource.objects.create(name="gamma")

        request = RequestFactory().post(
            "/release-resource/",
            data={
                "names": "alpha,beta,gamma",
                "owner": "batman",
            },
        )

        response = release_resource(request)
        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["message"] == "1 resources released. 2 unowned resources skipped."
        assert set(payload["missing"]) == set()
        assert set(payload["not_owned"]) == {"beta", "gamma"}
