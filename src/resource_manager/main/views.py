"""View functions for the main resource manager app."""

from django.http import HttpRequest, HttpResponse

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
            f"Name: '{res.name}', "
            f"Session ID: '{res.session_id}', "
            f"Session Name: '{res.session_name}', "
            f"User Name: '{res.user_name}'</br>"
        )

    return HttpResponse(message)
