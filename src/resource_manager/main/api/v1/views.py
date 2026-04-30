"""View functions for the resource manager API."""

from django.http import HttpRequest, JsonResponse

from ...models import Resource


def add_resource(request: HttpRequest) -> JsonResponse:
    """Add resources to the database.

    Args:
        request: HTTP POST request containing resource names.

    Returns:
        JSON response containing a status message and any failures.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        names = {n.strip() for n in request.POST["names"].split(",")}
    except KeyError:
        message = "Missing required argument 'names'."
        return JsonResponse({"message": message}, status=400)

    # Find duplicate resources.
    duplicate = Resource.objects.filter(name__in=names)
    duplicate_names = set(duplicate.values_list("name", flat=True))

    # Create new resources, skipping duplicates.
    added_names = [n for n in names if n not in duplicate_names]
    Resource.objects.bulk_create([Resource(name=n) for n in added_names])

    # Report results.
    message = ""
    if added_names:
        message += f"{len(added_names)} resources added. "
    if duplicate_names:
        message += f"{len(duplicate_names)} duplicate resources skipped. "
    message = message.strip()

    return JsonResponse(
        {"message": message, "added": added_names, "duplicate": list(duplicate_names)}, status=201
    )


def remove_resource(request: HttpRequest) -> JsonResponse:
    """Remove unowned resources from the database.

    Args:
        request: HTTP POST request containing resource names.

    Returns:
        JSON response containing a status message and any failures.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        names = {n.strip() for n in request.POST["names"].split(",")}
    except KeyError:
        message = "Missing required argument 'names'."
        return JsonResponse({"message": message}, status=400)

    # Find existing and missing resources.
    existing = Resource.objects.filter(name__in=names)
    existing_names = set(existing.values_list("name", flat=True))
    missing_names = names - existing_names

    # Find owned and unowned resources.
    existing_not_owned = existing.filter(owner__isnull=True)
    existing_not_owned_names = set(existing_not_owned.values_list("name", flat=True))
    existing_owned_names = existing_names - existing_not_owned_names

    # Only remove existing resources that are not owned.
    existing_not_owned.delete()

    # Report results.
    message = ""
    if existing_not_owned_names:
        message += f"{len(existing_not_owned_names)} resources removed. "
    if missing_names:
        message += f"{len(missing_names)} missing resources skipped. "
    if existing_owned_names:
        message += f"{len(existing_owned_names)} already-owned resources skipped. "
    message = message.strip()

    return JsonResponse(
        {
            "message": message,
            "removed": list(existing_not_owned_names),
            "missing": list(missing_names),
            "already_owned": list(existing_owned_names),
        },
        status=200,
    )


def query_resource(request: HttpRequest) -> JsonResponse:
    """Query resources in the database.

    Args:
        request: HTTP POST request containing resource names.

    Returns:
        JSON response containing a status message, the queried resources and any failures.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        names = {n.strip() for n in request.POST["names"].split(",")}
    except KeyError:
        message = "Missing required argument 'names'."
        return JsonResponse({"message": message}, status=400)

    # Find existing and missing resources.
    existing = Resource.objects.filter(name__in=names)
    existing_names = set(existing.values_list("name", flat=True))
    missing_names = names - existing_names

    # Build query list.
    queries = [
        {
            "name": r.name,
            "owner": r.owner,
            "session_id": r.session_id,
            "session_name": r.session_name,
        }
        for r in existing
    ]

    # Report results.
    message = ""
    if existing_names:
        message += f"{len(existing_names)} resources queried. "
    if missing_names:
        message += f"{len(missing_names)} missing resources skipped. "
    message = message.strip()

    return JsonResponse(
        {"message": message, "query_results": queries, "missing": list(missing_names)},
        status=200,
    )


def request_resource(request: HttpRequest) -> JsonResponse:
    """Request ownership of resources in the database.

    Args:
        request: HTTP POST request containing resource names, owner, session_name, session_id.

    Returns:
        JSON response containing a status message and any failures.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        names = {n.strip() for n in request.POST["names"].split(",")}
        owner = request.POST["owner"].strip()
        session_id = request.POST["session_id"].strip()
        session_name = request.POST["session_name"].strip()
    except KeyError as e:
        message = f"Missing required argument '{e.args[0]}'."
        return JsonResponse({"message": message}, status=400)

    # Find existing and missing resources.
    existing = Resource.objects.filter(name__in=names)
    existing_names = set(existing.values_list("name", flat=True))
    missing_names = names - existing_names

    # Fail early if any existing resources are already owned.
    existing_owned = existing.filter(owner__isnull=False)
    if existing_owned.exists():
        existing_owned_names = set(existing_owned.values_list("name", flat=True))
        message = "1 or more resources are already owned. Aborting."
        return JsonResponse(
            {
                "message": message,
                "taken": [],
                "missing": list(missing_names),
                "already_owned": list(existing_owned_names),
            },
            status=400,
        )

    # Take ownership of existing resources that are not owned.
    for resource in existing:
        resource.owner = owner
        resource.session_id = session_id
        resource.session_name = session_name
        resource.save()

    # Report results.
    message = ""
    if existing_names:
        message += f"{len(existing_names)} resources taken. "
    if missing_names:
        message += f"{len(missing_names)} missing resources skipped. "
    message = message.strip()

    return JsonResponse(
        {
            "message": message,
            "taken": list(existing_names),
            "missing": list(missing_names),
            "already_owned": [],
        },
        status=200,
    )


def release_resource(request: HttpRequest) -> JsonResponse:
    """Release ownership of resources in the database.

    Args:
        request: HTTP POST request containing resource names and owner.

    Returns:
        JSON response containing a status message and any failures.
    """
    if request.method != "POST":
        message = f"Only POST requests are allowed. Received '{request.method}'."
        return JsonResponse({"message": message}, status=400)

    try:
        names = {n.strip() for n in request.POST["names"].split(",")}
        owner = request.POST["owner"].strip()
    except KeyError as e:
        message = f"Missing required argument '{e.args[0]}'."
        return JsonResponse({"message": message}, status=400)

    # Find existing and missing resources.
    existing = Resource.objects.filter(name__in=names)
    existing_names = set(existing.values_list("name", flat=True))
    missing_names = names - existing_names

    # Release ownership of existing resources that are owned by <owner>.
    existing_not_owned_names = set()
    existing_owned_names = set()
    for resource in existing:
        if resource.owner == owner:
            existing_owned_names.add(resource.name)
            resource.owner = None
            resource.session_id = None
            resource.session_name = None
            resource.save()
        else:
            existing_not_owned_names.add(resource.name)

    # Report released, missing and already-owned resources.
    message = f"{len(existing_owned_names)} resources released."
    if missing_names:
        message += f" {len(missing_names)} missing resources skipped."
    if existing_not_owned_names:
        message += f" {len(existing_not_owned_names)} unowned resources skipped."

    return JsonResponse(
        {
            "message": message,
            "missing": list(missing_names),
            "not_owned": list(existing_not_owned_names),
        },
        status=200,
    )
