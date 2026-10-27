from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from clients.models import Client
from projects.models import Project

from .forms import TaskForm
from .models import Task


class TaskTests(TestCase):
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
        client = Client.objects.create(
            name="Acme", email="acme@example.com", phone="123", address="Main",
        )
        self.project = Project.objects.create(
            name="Project", client=client, start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        self.project.architects.add(self.architect)

    def test_form_requires_fields_and_limits_assignment_to_project_architects(self):
        form = TaskForm(project=self.project, data={
            "title": "Task", "description": "Description",
            "due_date": "2026-05-01", "architect": self.architect.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)
        task = form.save(commit=False)
        task.project = self.project
        task.save()
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.architect, self.architect)
        self.assertFalse(TaskForm(project=self.project, data={}).is_valid())

    def test_admin_can_create_update_delete_and_change_status(self):
        self.client.force_login(self.admin)
        data = {
            "title": "Task", "description": "Description",
            "due_date": "2026-05-01", "architect": self.architect.pk,
        }
        response = self.client.post(
            reverse("task_create", args=[self.project.pk]), data,
        )
        self.assertRedirects(
            response, reverse("project_task_list", args=[self.project.pk]),
        )
        task = Task.objects.get(title="Task")
        self.client.post(
            reverse("task_update", args=[self.project.pk, task.pk]),
            {**data, "title": "Updated"},
        )
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated")
        self.client.post(
            reverse("task_status_update", args=[self.project.pk, task.pk]),
            {"status": Task.Status.COMPLETED},
        )
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.COMPLETED)
        self.client.post(reverse("task_delete", args=[self.project.pk, task.pk]))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_assigned_architect_can_change_status_but_not_task_details(self):
        task = Task.objects.create(
            title="Task", description="Description", project=self.project,
            architect=self.architect, due_date=date(2026, 5, 1),
        )
        self.client.force_login(self.architect)
        response = self.client.post(
            reverse("task_status_update", args=[self.project.pk, task.pk]),
            {"status": Task.Status.IN_PROGRESS},
        )
        self.assertRedirects(response, reverse("project_task_list", args=[self.project.pk]))
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)
        self.assertEqual(
            self.client.get(reverse("task_update", args=[self.project.pk, task.pk])).status_code,
            403,
        )

    def test_deleting_project_cascades_to_tasks(self):
        task = Task.objects.create(
            title="Task", description="Description", project=self.project,
            architect=self.architect, due_date=date(2026, 5, 1),
        )
        self.project.delete()
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
