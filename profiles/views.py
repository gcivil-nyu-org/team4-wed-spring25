from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, PetProfile
from .forms import UserProfileForm, PetProfileForm
from django.http import HttpResponseForbidden, HttpResponse  # Import HttpResponse


@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    pets = PetProfile.objects.filter(owner=user_profile)
    return render(
        request, "profiles/profile.html", {"user_profile": user_profile, "pets": pets}
    )


@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user_profile)
    context = {
        "form": form,
        "object": user_profile,
    }
    return render(request, "profiles/edit_profile.html", context)


@login_required
def add_pet(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = user_profile
            pet.save()
            return redirect("profile")
    else:
        form = PetProfileForm()
    return render(request, "profiles/add_pet.html", {"form": form})


@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)

    if pet.owner.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this pet.")

    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = PetProfileForm(instance=pet)

    context = {
        "form": form,
        "object": pet,
    }
    return render(request, "profiles/edit_pet.html", context)


@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)
    if pet.owner.user != request.user:
        # Return 403 for GET requests too if user doesn't own the pet
        return HttpResponseForbidden("You do not have permission to delete this pet.")

    # Check if the request is AJAX
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if request.method == "POST":
        pet.delete()
        if is_ajax:
            return HttpResponse(
                status=204
            )  # Return 204 No Content for successful AJAX POST
        else:
            return redirect("profile")  # Redirect for non-AJAX POST

    # If GET request, redirect to profile instead of rendering a template
    # Or handle differently if you MUST have a confirmation page
    return redirect("profile")


@login_required
def pet_detail(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)
    return render(request, "profiles/pet_detail.html", {"pet": pet})
