# from django.shortcuts import render  # noqa: F401  # Ignore "imported but unused"
from django.http import HttpResponse
from django.http import JsonResponse

from django.db import connection


def test_db_connection(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        return JsonResponse({"status": "success", "message": "Database connected!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def health_check(request):
    return JsonResponse({"status": "ok"})
