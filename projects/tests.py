from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from clients.models import Client

from .forms import ProjectForm
from .models import Project


class ProjectTests(TestCase):
    def setUp(self):
        self.admin_group = Group.objects.get(name="Administrator")
        self.architect_group = Group.objects.get(name="Architect")
        self.admin = User.objects.create_user(
            email="admin@example.com", first_name="Admin", last_name="User",
            password="StrongPassword123!", role=User.Role.ADMIN,
        )
        self.admin.groups.add(self.admin_group)
        self.architect = User.objects.create_user(
            email="architect@example.com", first_name="Amina", last_name="Architect",
            password="StrongPassword123!", role=User.Role.ARCHITECT,
        )
        self.architect.groups.add(self.architect_group)
        self.client_record = Client.objects.create(
            name="Acme", email="acme@example.com", phone="123", address="Main",
        )

    def project(self, name="Project", status=Project.Status.PLANNED):
        return Project.objects.create(
            name=name, client=self.client_record,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            status=status,
        )

    def test_form_validates_required_fields_dates_and_assignments(self):
        form = ProjectForm(data={
            "name": "New", "description": "Description", "client": self.client_record.pk,
            "start_date": "2026-01-01", "end_date": "2026-12-31",
            "status": Project.Status.PLANNED, "architects": [self.architect.pk],
        })
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save()
        self.assertEqual(project.client, self.client_record)
        self.assertIn(self.architect, project.architects.all())

        invalid = ProjectForm(data={
            "name": "Invalid", "client": self.client_record.pk,
            "start_date": "2026-12-31", "end_date": "2026-01-01",
            "status": Project.Status.PLANNED,
        })
        self.assertFalse(invalid.is_valid())
        self.assertIn("end_date", invalid.errors)

    def test_admin_can_create_update_delete_and_change_status(self):
        self.client.force_login(self.admin)
        data = {
            "name": "Created", "description": "Description",
            "client": self.client_record.pk, "start_date": "2026-01-01",
            "end_date": "2026-12-31", "status": Project.Status.PLANNED,
            "architects": [self.architect.pk],
        }
        response = self.client.post(reverse("project_create"), data)
        self.assertRedirects(response, reverse("project_list"))
        project = Project.objects.get(name="Created")
        self.client.post(reverse("project_update", args=[project.pk]), {**data, "name": "Updated"})
        project.refresh_from_db()
        self.assertEqual(project.name, "Updated")
        self.client.post(
            reverse("project_status_update", args=[project.pk]),
            {"status": Project.Status.COMPLETED},
        )
        project.refresh_from_db()
        self.assertEqual(project.status, Project.Status.COMPLETED)
        self.assertRedirects(
            self.client.post(reverse("project_delete", args=[project.pk])),
            reverse("project_list"),
        )
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_architect_sees_only_assigned_projects_and_cannot_modify(self):
        assigned = self.project("Assigned")
        self.project("Other")
        assigned.architects.add(self.architect)
        self.client.force_login(self.architect)
        response = self.client.get(reverse("project_list"))
        self.assertEqual(list(response.context["projects"].object_list), [assigned])
        self.assertEqual(self.client.get(reverse("project_create")).status_code, 403)
