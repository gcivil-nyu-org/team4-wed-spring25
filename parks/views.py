from django.shortcuts import render
from django.http import HttpResponse
from .models import Park

def park_list(request):
    # Sample Data: List of dictionaries (no database required)
    parks = [
        {"prop_id": "P001", "name": "Central Park", "location": "Manhattan", "acres": 843.0, "status": "Open"},
        {"prop_id": "P002", "name": "Prospect Park", "location": "Brooklyn", "acres": 526.0, "status": "Open"},
        {"prop_id": "P003", "name": "Flushing Meadows", "location": "Queens", "acres": 897.0, "status": "Open"},
        {"prop_id": "P004", "name": "Battery Park", "location": "Manhattan", "acres": 25.0, "status": "Open"},
        {"prop_id": "P005", "name": "Riverside Park", "location": "Manhattan", "acres": 330.0, "status": "Open"},
        {"prop_id": "P006", "name": "Highland Park", "location": "Brooklyn", "acres": 101.0, "status": "Open"},
        {"prop_id": "P007", "name": "Van Cortlandt Park", "location": "Bronx", "acres": 1146.0, "status": "Open"},
        {"prop_id": "P008", "name": "Pelham Bay Park", "location": "Bronx", "acres": 2772.0, "status": "Open"},
        {"prop_id": "P009", "name": "McCarren Park", "location": "Brooklyn", "acres": 35.0, "status": "Open"},
        {"prop_id": "P010", "name": "Bronx Park", "location": "Bronx", "acres": 718.0, "status": "Open"},
        {"prop_id": "P011", "name": "Clove Lakes Park", "location": "Staten Island", "acres": 198.0, "status": "Open"},
        {"prop_id": "P012", "name": "Forest Park", "location": "Queens", "acres": 538.0, "status": "Open"},
        {"prop_id": "P013", "name": "Marine Park", "location": "Brooklyn", "acres": 798.0, "status": "Open"},
        {"prop_id": "P014", "name": "Washington Square Park", "location": "Manhattan", "acres": 9.8, "status": "Open"},
        {"prop_id": "P015", "name": "Astoria Park", "location": "Queens", "acres": 59.0, "status": "Open"},
        {"prop_id": "P016", "name": "Hudson River Park", "location": "Manhattan", "acres": 550.0, "status": "Open"},
        {"prop_id": "P017", "name": "Union Square Park", "location": "Manhattan", "acres": 6.0, "status": "Open"},
        {"prop_id": "P018", "name": "Tompkins Square Park", "location": "Manhattan", "acres": 10.5, "status": "Open"},
        {"prop_id": "P019", "name": "Bryant Park", "location": "Manhattan", "acres": 9.6, "status": "Open"},
        {"prop_id": "P020", "name": "Corona Park", "location": "Queens", "acres": 1255.0, "status": "Open"},
    ]

    return render(request, "parks/park_list.html", {"parks": parks})
