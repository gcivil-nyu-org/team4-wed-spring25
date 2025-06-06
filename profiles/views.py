from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse, Http404

from .models import UserProfile, PetProfile
from .forms import UserProfileForm, PetProfileForm
from parks.models import Review, Reply, ParkImage
from django.db.models import Prefetch, Q, OuterRef, Subquery, CharField
from django.db.models.functions import Cast
from accounts.decorators import ban_protected
from django.http import JsonResponse
from django.urls import reverse


@ban_protected
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=profile_user)
    pets = PetProfile.objects.filter(owner=user_profile)
    is_own_profile = request.user == profile_user

    if user_profile.is_banned:
        return render(
            request,
            "profiles/banned_profile.html",
            {"profile_user": profile_user, "pet_view": False},
        )

    thumbnail_subquery = ParkImage.objects.filter(
        park_id=OuterRef("park_id"),
        is_removed=False,
        review__is_removed=False,
    ).values("image")[:1]

    image_qs = ParkImage.objects.filter(is_removed=False)

    user_reviews = (
        Review.objects.filter(user=profile_user, is_removed=False)
        .select_related("park")
        .prefetch_related(
            Prefetch("images", queryset=image_qs, to_attr="visible_images")
        )
        .annotate(
            thumbnail_url=Cast(Subquery(thumbnail_subquery), output_field=CharField())
        )
    )

    user_replies = Reply.objects.filter(user=profile_user, is_deleted=False)
    user_images = ParkImage.objects.filter(user=profile_user, is_removed=False).filter(
        Q(review__isnull=True) | Q(review__is_deleted=False)
    )
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


@ban_protected
@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            redirect_url = reverse(
                "profiles:profile", kwargs={"username": request.user.username}
            )
            return JsonResponse({"success": True, "redirect_url": redirect_url})
        else:
            return JsonResponse(form.errors, status=400)
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        "form": form,
        "object": user_profile,
    }
    return render(request, "profiles/edit_profile.html", context)


@ban_protected
@login_required
def add_pet(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = user_profile
            pet.save()
            return redirect("profiles:profile", username=request.user.username)
    else:
        form = PetProfileForm()

    return render(request, "profiles/add_pet.html", {"form": form})


@ban_protected
@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)

    if pet.owner.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this pet.")

    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect("profiles:profile", username=request.user.username)
    else:
        form = PetProfileForm(instance=pet)

    context = {
        "form": form,
        "object": pet,
    }
    return render(request, "profiles/edit_pet.html", context)


@ban_protected
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
            return redirect("profiles:profile", username=pet_owner_username)

    return redirect("profiles:profile", username=pet.owner.user.username)


@ban_protected
@login_required
def pet_detail(request, username, pet_id):
    profile_user = get_object_or_404(User, username=username)
    pet = get_object_or_404(PetProfile, id=pet_id)

    if profile_user.userprofile.is_banned:
        return render(
            request,
            "profiles/banned_profile.html",
            {"profile_user": profile_user, "pet_view": True},
        )

    if pet.owner.user != profile_user:
        raise Http404("Pet not found for this user.")

    is_owner_viewing = request.user == profile_user

    context = {
        "pet": pet,
        "profile_user": profile_user,
        "is_owner_viewing": is_owner_viewing,
    }
    return render(request, "profiles/pet_detail.html", context)


@ban_protected
@login_required
def search_view(request):
    query = request.GET.get("q", "")

    search_type = request.GET.get("type", "users")
    submitted_breed = request.GET.get("breed", "")
    min_age = request.GET.get("min_age")
    max_age = request.GET.get("max_age")
    gender = request.GET.get("gender")
    has_photo = request.GET.get("has_photo")

    user_results = []
    pet_results = []
    ALLOWED_BREEDS = [
        "Beagle",
        "Border Collie",
        "Boston Terrier",
        "Boxer",
        "Bulldog",
        "Chihuahua",
        "Cocker Spaniel",
        "Dachshund",
        "Dalmatian",
        "Doberman",
        "French Bulldog",
        "German Shepherd",
        "Golden Retriever",
        "Great Dane",
        "Labrador Retriever",
        "Maltese",
        "Miniature Schnauzer",
        "Pembroke Welsh Corgi",
        "Pomeranian",
        "Poodle",
        "Pug",
        "Rottweiler",
        "Samoyed",
        "Shiba Inu",
        "Shih Tzu",
        "Siberian Husky",
        "Yorkshire Terrier",
        "Abyssinian",
        "American Shorthair",
        "Bengal",
        "Birman",
        "British Shorthair",
        "Exotic Shorthair",
        "Maine Coon",
        "Persian",
        "Ragdoll",
        "Russian Blue",
        "Scottish Fold",
        "Siamese",
        "Sphynx",
    ]
    breeds = sorted(ALLOWED_BREEDS)

    if not query and not submitted_breed:
        selected_breed_for_template = "all_breed"
    elif submitted_breed in ["", "none"]:
        selected_breed_for_template = "all_breed"
    else:
        selected_breed_for_template = submitted_breed

    if search_type == "users":
        if query:
            user_results = User.objects.filter(
                Q(username__icontains=query) | Q(userprofile__name__icontains=query),
                userprofile__is_banned=False,
            ).distinct()
        else:
            user_results = User.objects.none()

    elif search_type == "pets":
        pet_results = PetProfile.objects.filter(owner__is_banned=False)

        if query:
            pet_results = pet_results.filter(name__icontains=query)

        if submitted_breed and submitted_breed not in ["none", "all_breed", ""]:
            if submitted_breed in ALLOWED_BREEDS:
                pet_results = pet_results.filter(breed=submitted_breed)

        if min_age:
            try:
                pet_results = pet_results.filter(age__gte=int(min_age))
            except (ValueError, TypeError):
                pass
        if max_age:
            try:
                pet_results = pet_results.filter(age__lte=int(max_age))
            except (ValueError, TypeError):
                pass
        if gender:
            pet_results = pet_results.filter(gender=gender)
        if has_photo:
            pet_results = pet_results.exclude(pet_picture__isnull=True).exclude(
                pet_picture=""
            )

    return render(
        request,
        "profiles/search.html",
        {
            "query": query,
            "search_type": search_type,
            "selected_breed": selected_breed_for_template,
            "user_results": user_results,
            "pet_results": pet_results,
            "breeds": breeds,
            "submitted_breed": submitted_breed,
            "min_age": min_age,
            "max_age": max_age,
            "gender": gender,
            "has_photo": has_photo,
        },
    )
