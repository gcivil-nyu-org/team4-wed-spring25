# homepage/error_views.py
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
)


def trigger_400(request):
    return HttpResponseBadRequest()


def trigger_403(request):
    return HttpResponseForbidden()


def trigger_404(request):
    return HttpResponseNotFound()


def trigger_500(request):
    raise Exception("Intentional server error")
