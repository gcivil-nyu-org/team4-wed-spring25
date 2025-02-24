from django.shortcuts import render
from django.http import HttpResponse
from .models import Park

def park_list(request):
    parks = Park.objects.all()
    park_names = ', '.join([park.name for park in parks])
    return HttpResponse(f"Park List: {park_names}" if park_names else "No park data available")
