from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    """
    Decorator to ensure the user is logged in and is staff.
    If not, raises a PermissionDenied exception (403).
    """

    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to access this view.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
