from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Announcement
from .decorators import staff_required  # Use the custom decorator
from .forms import AnnouncementForm


def announcements_list(request):
    # Show only non-expired announcements
    announcements = (
        Announcement.objects.filter(expiry_date__isnull=True)
        .union(Announcement.objects.filter(expiry_date__gte=timezone.now()))
        .order_by("-pinned", "-created_at")
    )
    return render(request, "announcements/list.html", {"announcements": announcements})


@staff_required
def create_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            return redirect("announcements_list")
    else:
        form = AnnouncementForm()
    return render(request, "announcements/create.html", {"form": form})


@staff_required
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect("announcements_list")
    else:
        form = AnnouncementForm(instance=announcement)
    return render(
        request, "announcements/edit.html", {"form": form, "announcement": announcement}
    )


@staff_required
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    return redirect("announcements_list")
