from django.shortcuts import render
from django.shortcuts import redirect
from django.http import (  # noqa: F401  # Ignore "imported but unused"
    HttpResponseForbidden,
    HttpResponse,
    JsonResponse,
    HttpResponsePermanentRedirect,
)
from django.urls import reverse  # noqa: F401  # Ignore "imported but unused"

from django.contrib.auth import login
from .forms import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save but don't commit yet
            user = form.save(commit=False)
            # If they chose Admin, mark them as staff
            if form.cleaned_data["role"] == "admin":
                user.is_staff = True
            user.save()

            # Log the user in immediately
            login(request, user)
            request.session.save()
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
