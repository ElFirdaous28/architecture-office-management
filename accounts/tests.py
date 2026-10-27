from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clients.models import Client
from projects.models import Project
from tasks.models import Task

from .models import User


class AccountTestMixin:
    def user(self, email="user@example.com", role=User.Role.ASSISTANT, **kwargs):
        names = {
            User.Role.ADMIN: "Administrator",
            User.Role.ARCHITECT: "Architect",
            User.Role.ASSISTANT: "Assistant",
        }
        user = User.objects.create_user(
            email=email,
            first_name=kwargs.pop("first_name", "Test"),
            last_name=kwargs.pop("last_name", "User"),
            password=kwargs.pop("password", "StrongPassword123!"),
            role=role,
            **kwargs,
        )
        user.groups.add(Group.objects.get(name=names[role]))
        return user


class AuthenticationTests(AccountTestMixin, TestCase):
    def test_valid_login_and_logout(self):
        user = self.user(role=User.Role.ADMIN)
        response = self.client.post(
            reverse("login"),
            {"email": user.email, "password": "StrongPassword123!"},
        )
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(self.client.session.get("_auth_user_id"))
        self.assertRedirects(self.client.get(reverse("logout")), reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_invalid_inactive_and_deleted_login_fail(self):
        inactive = self.user(email="inactive@example.com", is_active=False)
        deleted = self.user(email="deleted@example.com", is_active=False)
        deleted.deleted_at = timezone.now()
        deleted.save(update_fields=["deleted_at"])
        for user in (inactive, deleted):
            response = self.client.post(
                reverse("login"),
                {"email": user.email, "password": "StrongPassword123!"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_pages_require_authentication(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

    def test_required_password_change_redirect_and_success(self):
        user = self.user(must_change_password=True)
        self.client.force_login(user)
        self.assertRedirects(
            self.client.get(reverse("dashboard")),
            reverse("password_change"),
        )
        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": "StrongPassword123!",
                "new_password1": "NewStrongPassword123!",
                "new_password2": "NewStrongPassword123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user.refresh_from_db()
        self.assertFalse(user.must_change_password)
        self.assertTrue(user.check_password("NewStrongPassword123!"))

    def test_password_change_rejects_wrong_current_password(self):
        user = self.user()
        self.client.force_login(user)
        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": "wrong",
                "new_password1": "NewStrongPassword123!",
                "new_password2": "NewStrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("StrongPassword123!"))

    def test_role_restricted_pages_return_forbidden(self):
        self.client.force_login(self.user(role=User.Role.ARCHITECT))
        self.assertEqual(self.client.get(reverse("user_list")).status_code, 403)

    def test_user_creation_assigns_role_and_forced_password_change(self):
        self.client.force_login(self.user(role=User.Role.ADMIN))
        response = self.client.post(
            reverse("user_create"),
            {
                "first_name": "Amina",
                "last_name": "Architect",
                "email": "amina@example.com",
                "role": "Architect",
            },
        )
        self.assertRedirects(response, reverse("user_list"))
        created = User.objects.get(email="amina@example.com")
        self.assertEqual(created.role, User.Role.ARCHITECT)
        self.assertTrue(created.must_change_password)
        self.assertTrue(created.groups.filter(name="Architect").exists())


class DashboardTests(AccountTestMixin, TestCase):
    def setUp(self):
        self.admin = self.user(email="admin@example.com", role=User.Role.ADMIN)
        self.client_record = Client.objects.create(
            name="Acme",
            email="acme@example.com",
            phone="0123456789",
            address="Main Street",
        )

    def project(self, status):
        return Project.objects.create(
            name=f"{status} project",
            client=self.client_record,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status=status,
        )

    def test_dashboard_counts_and_status_data(self):
        planned = self.project(Project.Status.PLANNED)
        active = self.project(Project.Status.IN_PROGRESS)
        self.project(Project.Status.COMPLETED)
        Task.objects.create(
            title="Done",
            description="Done",
            project=active,
            due_date=date(2026, 6, 1),
            status=Task.Status.COMPLETED,
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["total_projects"], 3)
        self.assertEqual(response.context["active_projects"], 1)
        self.assertEqual(response.context["completed_projects"], 1)
        self.assertEqual(response.context["total_tasks"], 1)
        self.assertEqual(response.context["completed_tasks"], 1)
        self.assertEqual(response.context["project_chart"]["data"], [1, 1, 1])
        self.assertEqual(planned.status, Project.Status.PLANNED)

    def test_empty_dashboard_is_valid(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_projects"], 0)
        self.assertEqual(response.context["recent_projects"].count(), 0)

    def test_soft_deleted_architect_is_excluded_from_dashboard(self):
        architect = self.user(
            email="deleted-architect@example.com",
            role=User.Role.ARCHITECT,
        )
        architect.deleted_at = timezone.now()
        architect.is_active = False
        architect.save(update_fields=["deleted_at", "is_active"])
        self.client.force_login(self.admin)
        response = self.client.get(reverse("dashboard"))
        self.assertNotIn(
            architect,
            list(response.context["available_architects_list"])
            + list(response.context["busiest_architects"]),
        )
