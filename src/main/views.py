from django.http import HttpRequest, HttpResponse, JsonResponse

from .models import Resource


def index(request: HttpRequest) -> HttpResponse:
    all_resources = Resource.objects.all()

    message = ""
    if request.user.is_authenticated:
        message += f"Hello {request.user.username}. "
    message += "You are at the index.</br></br>"
    for res in all_resources:
        message += f"Name: {res.name},  Owner: {res.owner}</br>"

    return HttpResponse(message)


def add_resource(request: HttpRequest) -> JsonResponse:
    name = request.POST.get("name")
    resource = Resource.objects.create(name=name)

    return JsonResponse({
        "name": resource.name,
        "owner": resource.owner,
    })


def query_resource(request: HttpRequest) -> JsonResponse:
    name = request.POST.get("name")
    resource = Resource.objects.get(name=name)

    return JsonResponse({
        "name": resource.name,
        "owner": resource.owner,
    })


def take_resource(request: HttpRequest) -> JsonResponse:
    name = request.POST.get("name")
    resource = Resource.objects.get(name=name)

    # TODO: view to handle sessions AND bearer tokens.
    username = "PLACEHOLDER_OWNER"
    resource.owner = username
    resource.save()

    return JsonResponse({
        "name": resource.name,
        "owner": resource.owner,
    })


def release_resource(request: HttpRequest) -> JsonResponse:
    name = request.POST.get("name")
    resource = Resource.objects.get(name=name)

    resource.owner = None
    resource.save()

    return JsonResponse({
        "name": resource.name,
        "owner": resource.owner,
    })
