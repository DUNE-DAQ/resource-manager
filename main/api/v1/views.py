"""View functions for the resource manager API."""

from django.forms.models import model_to_dict
from django.http import HttpRequest, JsonResponse

from ...models import Resource


def add_resource(request: HttpRequest) -> JsonResponse:
    """Add a resource to the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing resource names.

    Returns:
        JSON response containing the created resource or an error message.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        names = request.POST["names"].split(",")
    except KeyError:
        message = "Missing required argument 'names'."
        return JsonResponse({"message": message}, status=400)

    # Find duplicate names.
    duplicates = set(Resource.objects.filter(name__in=names).values_list("name", flat=True))

    # Create new resources, skipping duplicates.
    new_names = [n for n in names if n not in duplicates]
    Resource.objects.bulk_create([Resource(name=n) for n in new_names])

    # Report new and duplicate resources.
    message = f"{len(new_names)} new resources added."
    if duplicates:
        message += f" {len(duplicates)} duplicate resources skipped."

    return JsonResponse({"message": message, "duplicates": list(duplicates)}, status=201)


def remove_resource(request: HttpRequest) -> JsonResponse:
    """Remove an unowned resource from the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing the resource's name.

    Returns:
        JSON response containing a success or error message.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        name = request.POST["name"]
    except KeyError:
        message = "Missing required argument 'name'."
        return JsonResponse({"message": message}, status=400)

    try:
        resource = Resource.objects.get(name=name)
    except Resource.DoesNotExist:
        message = f"Resource '{name}' does not exist."
        return JsonResponse({"message": message}, status=404)

    # Check that the resource is not owned before removing it.
    if resource.owner is not None:
        message = f"Resource '{name}' is currently owned by '{resource.owner}'."
        return JsonResponse({"message": message}, status=400)

    resource.delete()

    return JsonResponse({"message": f"Resource '{name}' removed successfully."})


def query_resource(request: HttpRequest) -> JsonResponse:
    """Query a resource from the database using a HTTP POST request.

    Args:
        request: HTTP POST request containing the resource's name.

    Returns:
        JSON response containing the queried resource.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        name = request.POST["name"]
    except KeyError:
        message = "Missing required argument 'name'."
        return JsonResponse({"message": message}, status=400)

    try:
        resource = Resource.objects.get(name=name)
    except Resource.DoesNotExist:
        message = f"Resource '{name}' does not exist."
        return JsonResponse({"message": message}, status=404)

    return JsonResponse(model_to_dict(resource))


def take_resource(request: HttpRequest) -> JsonResponse:
    """Take ownership of a resource using a HTTP POST request.

    Args:
        request: HTTP POST request containing name, owner, session_name and session_id.

    Returns:
        JSON response containing the resource with updated ownership.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        name = request.POST["name"]
        owner = request.POST["owner"]
        session_id = request.POST["session_id"]
        session_name = request.POST["session_name"]
    except KeyError as e:
        message = f"Missing required argument '{e.args[0]}'."
        return JsonResponse({"message": message}, status=400)

    try:
        resource = Resource.objects.get(name=name)
    except Resource.DoesNotExist:
        message = f"Resource '{name}' does not exist."
        return JsonResponse({"message": message}, status=404)

    # Check that the resource is not owned before taking it.
    if resource.owner is not None:
        message = f"Resource '{name}' is currently owned by '{resource.owner}'."
        return JsonResponse({"message": message}, status=400)

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
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        name = request.POST["name"]
    except KeyError:
        message = "Missing required argument 'name'."
        return JsonResponse({"message": message}, status=400)

    try:
        resource = Resource.objects.get(name=name)
    except Resource.DoesNotExist:
        message = f"Resource '{name}' does not exist."
        return JsonResponse({"message": message}, status=404)

    # Check that the resource is owned before releasing it.
    if resource.owner is None:
        message = f"Resource '{name}' is not currently owned."
        return JsonResponse({"message": message}, status=400)

    resource.owner = None
    resource.session_id = None
    resource.session_name = None
    resource.save()

    return JsonResponse(model_to_dict(resource))
