from django.shortcuts import render
from django.http import HttpResponse
from .models import Park
from django.shortcuts import render
from .models import DogRun

def park_list(request):
    parks = DogRun.objects.all()  # Fetch all dog runs from the database
    return render(request, "parks/park_list.html", {"parks": parks})
