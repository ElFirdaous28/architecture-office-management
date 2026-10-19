
from django.shortcuts import redirect
from django.urls import resolve


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and getattr(request.user, "deleted_at", None) is not None
        ):
            from django.contrib.auth import logout

            logout(request)
            return redirect("login")

        if (
            request.user.is_authenticated
            and getattr(request.user, "must_change_password", False)
        ):
            allowed_urls = {"login", "logout", "password_change"}

            try:
                url_name = resolve(request.path_info).url_name
            except Exception:
                url_name = None

            if url_name not in allowed_urls:
                return redirect("password_change")

        return self.get_response(request)