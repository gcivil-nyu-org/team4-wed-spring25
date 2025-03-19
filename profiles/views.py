from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, PetProfile
from .forms import UserProfileForm, PetProfileForm

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    pets = PetProfile.objects.filter(owner=user_profile)
    return render(request, 'profiles/profile.html', {'user_profile': user_profile, 'pets': pets})

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'profiles/edit_profile.html', {'form': form})

@login_required
def add_pet(request):
    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = UserProfile.objects.get(user=request.user)
            pet.save()
            return redirect('profile')
    else:
        form = PetProfileForm()
    return render(request, 'profiles/add_pet.html', {'form': form})

@login_required
def edit_pet(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)
    if request.method == "POST":
        form = PetProfileForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PetProfileForm(instance=pet)
    return render(request, 'profiles/edit_pet.html', {'form': form})

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)
    if request.method == "POST":
        pet.delete()
        return redirect('profile')
    return render(request, 'profiles/delete_pet.html', {'pet': pet})

@login_required
def pet_detail(request, pet_id):
    pet = get_object_or_404(PetProfile, id=pet_id)
    return render(request, 'profiles/pet_detail.html', {'pet': pet})
