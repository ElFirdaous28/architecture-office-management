from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from .models import User
from clients.models import Client
from projects.models import Project
from tasks.models import Task

from .decorators import role_required
from .forms import ProfileForm, RequiredPasswordChangeForm, UserCreateForm

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q, Count


@login_required
def profile_view(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_account":
            request.user.deleted_at = timezone.now()
            request.user.is_active = False
            request.user.save(update_fields=["deleted_at", "is_active"])
            logout(request)
            return redirect("login")
        if action == "profile":
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, _("Profile updated successfully."))
                return redirect("profile")
        elif action == "password":
            password_form = PasswordChangeForm(
                user=request.user,
                data=request.POST,
            )
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, _("Password updated successfully."))
                return redirect("profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
        },
    )


@login_required
def required_password_change_view(request):
    password_form = RequiredPasswordChangeForm(user=request.user)

    if request.method == "POST":
        password_form = RequiredPasswordChangeForm(
            user=request.user,
            data=request.POST,
        )
        if password_form.is_valid():
            password_form.save()
            request.user.must_change_password = False
            request.user.save(update_fields=["must_change_password"])
            update_session_auth_hash(request, request.user)
            messages.success(request, _("Password updated successfully."))
            return redirect("dashboard")

    return render(
        request,
        "accounts/change_password.html",
        {"password_form": password_form},
    )

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
            {'error': _('Invalid email or password.')}
        )

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    user = request.user
    groups = set(user.groups.values_list("name", flat=True))

    context = {
        "total_clients": Client.objects.count(),
        "total_projects": Project.objects.count(),
        "total_tasks": Task.objects.count(),
        "completed_projects": Project.objects.filter(
            status=Project.Status.COMPLETED
        ).count(),
        "completed_tasks": Task.objects.filter(
            status=Task.Status.COMPLETED
        ).count(),
        "user_role": next(
            (
                name
                for name in ("Administrator", "Architect", "Assistant")
                if name in groups
            ),
            "No role assigned",
        ),
        "is_administrator": "Administrator" in groups,
        "is_architect": "Architect" in groups,
        "is_assistant": "Assistant" in groups,
    }

    if "Administrator" in groups:
        context["active_projects"] = Project.objects.filter(
            status=Project.Status.IN_PROGRESS
        ).count()

        project_status_counts = dict(
            Project.objects.values_list("status").annotate(
                total=Count("id")
            ).values_list("status", "total")
        )

        context["project_chart"] = {
            "labels": [str(label) for value, label in Project.Status.choices],
            "data": [
                project_status_counts.get(value, 0)
                for value, label in Project.Status.choices
            ],
        }

        task_status_counts = dict(
            Task.objects.values_list("status").annotate(
                total=Count("id")
            ).values_list("status", "total")
        )

        context["task_chart"] = {
            "labels": [str(label) for value, label in Task.Status.choices],
            "data": [
                task_status_counts.get(value, 0)
                for value, label in Task.Status.choices
            ],
        }

        context["recent_projects"] = (
            Project.objects.select_related("client")
            .prefetch_related("architects")
            .order_by("-updated_at")[:5]
        )

        architects = (
            User.objects.filter(
                role=User.Role.ARCHITECT,
                is_active=True,
                deleted_at__isnull=True,
            )
            .annotate(
                active_project_count=Count(
                    "assigned_projects",
                    filter=Q(
                        assigned_projects__status=Project.Status.IN_PROGRESS
                    ),
                    distinct=True,
                )
            )
            .order_by("last_name", "first_name")
        )

        context["available_architects_list"] = architects.filter(
            active_project_count=0
        )[:3]

        context["busiest_architects"] = architects.filter(
            active_project_count__gt=0
        ).order_by(
            "-active_project_count", "last_name", "first_name"
        )[:3]

        template_name = "accounts/dashboards/administrator.html"

   
    elif "Architect" in groups:
        my_projects = Project.objects.filter(architects=user)
        my_tasks = Task.objects.filter(architect=user)

        context["my_projects"] = my_projects
        context["my_tasks"] = my_tasks
        context["my_active_projects"] = my_projects.filter(
            status=Project.Status.IN_PROGRESS
        ).count()
        context["my_completed_tasks"] = my_tasks.filter(
            status=Task.Status.COMPLETED
        ).count()

        context["upcoming_tasks"] = (
            my_tasks.exclude(status=Task.Status.COMPLETED)
            .order_by("due_date")[:5]
        )

        task_status_counts = {
            item["status"]: item["total"]
            for item in my_tasks.values("status").annotate(total=Count("id"))
        }

        context["task_chart"] = {
            "labels": [str(label) for value, label in Task.Status.choices],
            "data": [
                task_status_counts.get(value, 0)
                for value, label in Task.Status.choices
            ],
        }

        template_name = "accounts/dashboards/architect.html"


    elif "Assistant" in groups:
        context["recent_projects"] = (
            Project.objects.select_related("client")
            .order_by("-updated_at")[:5]
        )

        project_status_counts = {
            item["status"]: item["total"]
            for item in Project.objects.values("status").annotate(
                total=Count("id")
            )
        }

        context["project_chart"] = {
            "labels": [
                str(label) for value, label in Project.Status.choices
            ],
            "data": [
                project_status_counts.get(value, 0)
                for value, label in Project.Status.choices
            ],
        }

        template_name = "accounts/dashboards/assistant.html"

    else:
        raise PermissionDenied

    return render(request, template_name, context)

@role_required("Administrator")
def user_list_view(request):
    search = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()
    users = User.objects.filter(deleted_at__isnull=True).prefetch_related("groups").order_by(
        "last_name", "first_name"
    )
    if search:
        users = users.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )
    if role in dict(User.Role.choices):
        users = users.filter(role=role)

    page_obj = Paginator(users, 10).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(
        request,
        "accounts/users/list.html",
        {
            "users": page_obj,
            "page_obj": page_obj,
            "query_params": query_params.urlencode(),
            "search": search,
            "role": role,
            "role_choices": User.Role.choices,
        },
    )


@role_required("Administrator")
def user_delete_view(request, pk):
    if request.method != "POST":
        raise PermissionDenied

    user = get_object_or_404(User.objects.filter(deleted_at__isnull=True), pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, _("You cannot delete your own account from the users table."))
        return redirect("user_list")

    user.deleted_at = timezone.now()
    user.is_active = False
    user.save(update_fields=["deleted_at", "is_active"])
    messages.success(request, _("User scheduled for deletion in 30 days."))
    return redirect("user_list")


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