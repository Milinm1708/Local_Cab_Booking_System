from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restrict a view to users whose .role is in `roles`."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, "You don't have permission to access that page.")
                return redirect('accounts:redirect_after_login')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
