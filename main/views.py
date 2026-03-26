"""View functions for the main resource manager app."""

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
        message += f"Name: {res.name},  Owner: {res.owner}</br>"

    return HttpResponse(message)


def add_resource(request: HttpRequest) -> JsonResponse:
    """Add a resource to the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing owner, resource_name, session_name and session_id.

    Returns:
        JSON response containing the created resource or an error message.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    resource_name = request.POST.get("resource_name")
    resource = Resource.objects.create(name=resource_name)

    return JsonResponse(
        {
            "resource_name": resource.name,
            "owner": resource.owner,
        }
    )


def query_resource(request: HttpRequest) -> JsonResponse:
    """Query a resource from the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing resource_name.

    Returns:
        JSON response containing the queried resource.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    resource_name = request.POST.get("resource_name")
    resource = Resource.objects.get(name=resource_name)

    return JsonResponse(
        {
            "resource_name": resource.name,
            "owner": resource.owner,
        }
    )


def take_resource(request: HttpRequest) -> JsonResponse:
    """Take ownership of a resource using a HTTP POST request.

    Args:
        request: HTTP POST request containing resource_name.

    Returns:
        JSON response containing the resource with updated ownership.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    resource_name = request.POST.get("resource_name")
    resource = Resource.objects.get(name=resource_name)

    # TODO: view to handle sessions AND bearer tokens.
    username = "PLACEHOLDER_OWNER"
    resource.owner = username
    resource.save()

    return JsonResponse(
        {
            "resource_name": resource.name,
            "owner": resource.owner,
        }
    )


def release_resource(request: HttpRequest) -> JsonResponse:
    """Release ownership of a resource using a HTTP POST request.

    Args:
        request: HTTP POST request containing resource_name.

    Returns:
        JSON response containing the resource with updated ownership.
    """
    if request.method != "POST":
        error_string = f"Only POST requests are allowed. Received {request.method}."
        return JsonResponse({"error": error_string}, status=400)

    resource_name = request.POST.get("resource_name")
    resource = Resource.objects.get(name=resource_name)

    resource.owner = None
    resource.save()

    return JsonResponse(
        {
            "resource_name": resource.name,
            "owner": resource.owner,
        }
    )
