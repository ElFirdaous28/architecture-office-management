
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_groups):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.groups.filter(
                name__in=allowed_groups
            ).exists():
                raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator