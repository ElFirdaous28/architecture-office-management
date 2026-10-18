from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .models import User
from clients.models import Client
from projects.models import Project
from tasks.models import Task

from .decorators import role_required
from .forms import RequiredPasswordChangeForm, UserCreateForm

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction


class RequiredPasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'accounts/change_password.html'
    form_class = RequiredPasswordChangeForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        user.must_change_password = False
        user.save(update_fields=['password', 'must_change_password'])
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(
            request,
            'accounts/login.html',
            {'error': 'Invalid email or password.'}
        )

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    groups = set(user.groups.values_list('name', flat=True))

    context = {
        'total_clients': Client.objects.count(),
        'total_projects': Project.objects.count(),
        'total_tasks': Task.objects.count(),
        'completed_projects': Project.objects.filter(
            status=Project.Status.COMPLETED
        ).count(),
        'completed_tasks': Task.objects.filter(
            status=Task.Status.COMPLETED
        ).count(),
        'user_role': next(
            (
                name
                for name in ('Administrator', 'Architect', 'Assistant')
                if name in groups
            ),
            'No role assigned',
        ),
        'is_administrator': 'Administrator' in groups,
        'is_architect': 'Architect' in groups,
        'is_assistant': 'Assistant' in groups,
    }

    if 'Architect' in groups:
        context['my_projects'] = Project.objects.filter(
            architects=user
        )
        context['my_tasks'] = Task.objects.filter(
            architect=user
        )

    if 'Administrator' in groups:
        template_name = 'accounts/dashboards/administrator.html'
    elif 'Architect' in groups:
        template_name = 'accounts/dashboards/architect.html'
    elif 'Assistant' in groups:
        template_name = 'accounts/dashboards/assistant.html'
    else:
        raise PermissionDenied

    return render(request, template_name, context)


@role_required("Administrator")
def user_list_view(request):
    users = User.objects.prefetch_related("groups").order_by(
        "last_name", "first_name"
    )

    return render(
        request,
        "accounts/users/list.html",
        {"users": users},
    )


@role_required("Administrator")
def user_create_view(request):
    form = UserCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()

                sent = send_mail(
                    subject="Your Architecture Office account",
                    message=(
                        f"Hello {user.first_name},\n\n"
                        "Your account has been created.\n\n"
                        f"Email: {user.email}\n"
                        f"Temporary password: {form.generated_password}\n\n"
                        "Please keep these credentials private.\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                if sent != 1:
                    raise RuntimeError("The email was not sent.")

        except Exception:
            form.add_error(
                None,
                "The account could not be created because the email "
                "could not be sent. Please check the email configuration "
                "and try again.",
            )
        else:
            messages.success(
                request,
                f"Account created and credentials emailed to {user.email}.",
            )
            return redirect("user_list")

    return render(
        request,
        "accounts/users/create.html",
        {"form": form},
    )