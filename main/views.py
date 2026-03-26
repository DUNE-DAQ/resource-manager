"""View functions for the main resource manager app."""

from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, JsonResponse

from .models import Resource


def index(request: HttpRequest) -> HttpResponse:
    """View function for the index page of the resource manager app.

    Args:
        request: HTTP GET request.

    Returns:
        HTTP response containing the index page.
    """
    if request.method != "GET":
        return HttpResponse("Page not found")

    all_resources = Resource.objects.all()

    message = ""
    if request.user.is_authenticated:
        message += f"Hello {request.user.get_username()}. "
    message += "You are at the index.</br></br>"
    for res in all_resources:
        message += (
            f"Name: {res.name}, "
            f"Owner: {res.owner}, "
            f"Session ID: {res.session_id}, "
            f"Session Name: {res.session_name}</br>"
        )

    return HttpResponse(message)


def add_resource(request: HttpRequest) -> JsonResponse:
    """Add a resource to the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing the resource's name.

    Returns:
        JSON response containing the created resource or an error message.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    # TODO: argument validation and error handling.
    name = request.POST.get("name")

    resource = Resource.objects.create(name=name)

    return JsonResponse(model_to_dict(resource))


def query_resource(request: HttpRequest) -> JsonResponse:
    """Query a resource from the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing the resource's name.

    Returns:
        JSON response containing the queried resource.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    # TODO: argument validation and error handling.
    name = request.POST.get("name")

    resource = Resource.objects.get(name=name)

    return JsonResponse(model_to_dict(resource))


def take_resource(request: HttpRequest) -> JsonResponse:
    """Take ownership of a resource using a HTTP POST request.

    Args:
        request: HTTP POST request containing name, owner, session_name and session_id.

    Returns:
        JSON response containing the resource with updated ownership.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    # TODO: argument validation and error handling.
    name = request.POST.get("name")
    owner = request.POST.get("owner")
    session_id = request.POST.get("session_id")
    session_name = request.POST.get("session_name")

    resource = Resource.objects.get(name=name)
    resource.owner = owner
    resource.session_id = session_id
    resource.session_name = session_name
    resource.save()

    return JsonResponse(model_to_dict(resource))


def release_resource(request: HttpRequest) -> JsonResponse:
    """Release ownership of a resource using a HTTP POST request.

    Args:
        request: HTTP POST request containing the resource's name.

    Returns:
        JSON response containing the resource with updated ownership.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    # TODO: argument validation and error handling.
    name = request.POST.get("name")

    resource = Resource.objects.get(name=name)
    resource.owner = None
    resource.session_id = None
    resource.session_name = None
    resource.save()

    return JsonResponse(model_to_dict(resource))
