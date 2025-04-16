from django.shortcuts import render
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)


def trigger_400(request):
    return HttpResponseBadRequest(render(request, "400.html"))


def trigger_403(request):
    return HttpResponseForbidden(render(request, "403.html"))


def trigger_404(request, exception=None):
    return HttpResponseNotFound(render(request, "404.html"))


def trigger_500(request):
    return HttpResponseServerError(render(request, "500.html"))
