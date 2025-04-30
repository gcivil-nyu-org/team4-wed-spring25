from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from accounts.utils import is_user_banned
from django.contrib.auth import logout


def ban_protected(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if is_user_banned(request.user):
            logout(request)
            messages.error(
                request,
                "Your account is banned. "
                "You cannot perform this action. You have been logged out.",
            )
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper
