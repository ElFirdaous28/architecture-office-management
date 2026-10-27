from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from clients.forms import ClientForm
from clients.models import Client
from projects.models import Project


class ClientTestMixin:
    def create_user(
        self,
        email="user@example.com",
        role=User.Role.ASSISTANT,
        **extra_fields,
    ):
        group_name = {
            User.Role.ADMIN: "Administrator",
            User.Role.ARCHITECT: "Architect",
            User.Role.ASSISTANT: "Assistant",
        }[role]
        Group.objects.get_or_create(name=group_name)

        password = extra_fields.pop("password", "StrongPassword123!")
        user = User.objects.create_user(
            email=email,
            first_name=extra_fields.pop("first_name", "Test"),
            last_name=extra_fields.pop("last_name", "User"),
            password=password,
            role=role,
            **extra_fields,
        )
        user.groups.set([Group.objects.get(name=group_name)])
        return user


class ClientFormTests(ClientTestMixin, TestCase):
    def test_client_model_form_validates_required_fields_and_email(self):
        invalid_form = ClientForm(
            data={
                "name": "",
                "email": "not-an-email",
                "phone": "",
                "address": "",
            }
        )

        self.assertFalse(invalid_form.is_valid())
        for field in ["name", "email", "phone", "address"]:
            self.assertIn(field, invalid_form.errors)

        valid_form = ClientForm(
            data={
                "name": "Acme Studio",
                "email": "acme@example.com",
                "phone": "+1 555 123 4567",
                "address": "123 Market Street",
            }
        )

        self.assertTrue(valid_form.is_valid(), valid_form.errors)
        self.assertEqual(valid_form.cleaned_data["email"], "acme@example.com")


class ClientManagementTests(ClientTestMixin, TestCase):
    def setUp(self):
        self.admin = self.create_user(email="admin@example.com", role=User.Role.ADMIN)
        self.assistant = self.create_user(
            email="assistant@example.com",
            role=User.Role.ASSISTANT,
        )

    def test_admin_can_create_and_update_a_client(self):
        self.client.force_login(self.admin)

        create_response = self.client.post(
            reverse("client_create"),
            {
                "name": "Acme Studio",
                "email": "acme@example.com",
                "phone": "+1 555 123 4567",
                "address": "123 Market Street",
            },
        )

        self.assertRedirects(create_response, reverse("client_list"))
        client = Client.objects.get(email="acme@example.com")
        self.assertEqual(client.name, "Acme Studio")

        update_response = self.client.post(
            reverse("client_update", args=[client.pk]),
            {
                "name": "Updated Acme",
                "email": "updated@example.com",
                "phone": "+1 555 765 4321",
                "address": "456 New Avenue",
            },
        )

        self.assertRedirects(update_response, reverse("client_list"))
        client.refresh_from_db()
        self.assertEqual(client.name, "Updated Acme")
        self.assertEqual(client.email, "updated@example.com")

    def test_allowed_roles_can_view_list_and_search_by_name_email_or_phone(self):
        self.client.force_login(self.assistant)

        acme = Client.objects.create(
            name="Acme Studio",
            email="acme.build@example.com",
            phone="555-0100",
            address="1 Main Street",
        )
        bluebird = Client.objects.create(
            name="Bluebird Builders",
            email="bluebird@example.com",
            phone="555-9999",
            address="2 Side Street",
        )

        response = self.client.get(reverse("client_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["clients"].object_list), [acme, bluebird])

        name_response = self.client.get(reverse("client_list"), {"q": "acme"})
        self.assertEqual(list(name_response.context["clients"].object_list), [acme])

        email_response = self.client.get(reverse("client_list"), {"q": "bluebird@example.com"})
        self.assertEqual(list(email_response.context["clients"].object_list), [bluebird])

        phone_response = self.client.get(reverse("client_list"), {"q": "555-9999"})
        self.assertEqual(list(phone_response.context["clients"].object_list), [bluebird])

    def test_unauthenticated_users_are_redirected_and_non_admins_are_forbidden(self):
        response = self.client.get(reverse("client_create"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('client_create')}",
        )

        client = Client.objects.create(
            name="Blocked Client",
            email="blocked@example.com",
            phone="555-1111",
            address="10 Block Way",
        )
        self.client.force_login(self.assistant)

        self.assertEqual(self.client.get(reverse("client_create")).status_code, 403)
        self.assertEqual(self.client.get(reverse("client_update", args=[client.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse("client_delete", args=[client.pk])).status_code, 403)
        self.assertEqual(
            self.client.post(
                reverse("client_create"),
                {
                    "name": "Oops",
                    "email": "oops@example.com",
                    "phone": "555",
                    "address": "Nope",
                },
            ).status_code,
            403,
        )

    def test_state_changing_client_requests_require_csrf(self):
        csrf_client = self.client_class(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)

        response = csrf_client.post(
            reverse("client_create"),
            {
                "name": "Blocked",
                "email": "csrf@example.com",
                "phone": "555-0000",
                "address": "No Street",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Client.objects.filter(email="csrf@example.com").exists())

    def test_client_delete_is_blocked_while_related_projects_exist(self):
        self.client.force_login(self.admin)
        client = Client.objects.create(
            name="Project Client",
            email="project-client@example.com",
            phone="555-3333",
            address="98 Anchor Drive",
        )
        Project.objects.create(
            name="Client Project",
            client=client,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status=Project.Status.PLANNED,
        )

        response = self.client.post(reverse("client_delete", args=[client.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "associated projects")
        self.assertTrue(Client.objects.filter(pk=client.pk).exists())

    def test_client_delete_succeeds_when_no_projects_are_linked(self):
        self.client.force_login(self.admin)
        client = Client.objects.create(
            name="Safe Client",
            email="safe@example.com",
            phone="555-4444",
            address="17 River Lane",
        )

        response = self.client.post(reverse("client_delete", args=[client.pk]))

        self.assertRedirects(response, reverse("client_list"))
        self.assertFalse(Client.objects.filter(pk=client.pk).exists())
