from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse, Http404

from .models import UserProfile, PetProfile
from .forms import UserProfileForm, PetProfileForm
from parks.models import Review, Reply, ParkImage


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=profile_user)
    pets = PetProfile.objects.filter(owner=user_profile)
    is_own_profile = request.user == profile_user

    user_reviews = Review.objects.filter(user=profile_user, is_removed=False)
    user_replies = Reply.objects.filter(user=profile_user)
    user_images = ParkImage.objects.filter(user=profile_user, is_removed=False)

    context = {
        "profile_user": profile_user,
        "user_profile": user_profile,
        "pets": pets,
        "is_own_profile": is_own_profile,
        "user_reviews": user_reviews,
        "user_replies": user_replies,
        "user_images": user_images,
    }
    return render(request, "profiles/profile.html", context)


@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("profile", username=request.user.username)
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        "form": form,
        "object": user_profile,
    }

    return render(request, "profiles/edit_profile.html", context)


@login_required
def add_pet(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = user_profile
            pet.save()
            return redirect("profile", username=request.user.username)
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
            return redirect("profile", username=request.user.username)
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
        return HttpResponseForbidden("You do not have permission to delete this pet.")

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if request.method == "POST":
        pet_owner_username = pet.owner.user.username
        pet.delete()
        if is_ajax:
            return HttpResponse(status=204)
        else:
            return redirect("profile", username=pet_owner_username)

    return redirect("profile", username=pet.owner.user.username)


@login_required
def pet_detail(request, username, pet_id):
    profile_user = get_object_or_404(User, username=username)
    pet = get_object_or_404(PetProfile, id=pet_id)

    if pet.owner.user != profile_user:
        raise Http404("Pet not found for this user.")

    is_owner_viewing = request.user == profile_user

    context = {
        "pet": pet,
        "profile_user": profile_user,
        "is_owner_viewing": is_owner_viewing,
    }
    return render(request, "profiles/pet_detail.html", context)
