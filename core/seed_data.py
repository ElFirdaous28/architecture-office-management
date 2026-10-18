from datetime import date

from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.db import transaction

from accounts.models import User
from clients.models import Client
from projects.models import Project
from tasks.models import Task


ROLE_GROUPS = {
    User.Role.ADMIN: "Administrator",
    User.Role.ARCHITECT: "Architect",
    User.Role.ASSISTANT: "Assistant",
}
SEED_PASSWORD = "ChangeMe123!"


def clean_database():
    Task.objects.all().delete()
    Project.objects.all().delete()
    Client.objects.all().delete()
    User.objects.all().delete()
    Session.objects.all().delete()


@transaction.atomic
def seed_database():
    groups = {
        role: Group.objects.get_or_create(name=group_name)[0]
        for role, group_name in ROLE_GROUPS.items()
    }

    users = {}
    user_data = [
        ("admin@example.com", "Admin", "User", User.Role.ADMIN),
        ("amina.architect@example.com", "Amina", "Haddad", User.Role.ARCHITECT),
        ("youssef.architect@example.com", "Youssef", "Mansouri", User.Role.ARCHITECT),
        ("sara.assistant@example.com", "Sara", "Bennani", User.Role.ASSISTANT),
    ]

    for email, first_name, last_name, role in user_data:
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "is_active": True,
                "must_change_password": False,
            },
        )
        user.set_password(SEED_PASSWORD)
        user.save(update_fields=["password"])
        user.groups.set([groups[role]])
        users[email] = user

    clients = [
        Client.objects.create(
            name="Atlas Developments",
            email="contact@atlas.example.com",
            phone="+213 555 010 101",
            address="12 Boulevard des Pins, Algiers",
        ),
        Client.objects.create(
            name="Northline Properties",
            email="hello@northline.example.com",
            phone="+213 555 010 202",
            address="8 Rue des Oliviers, Oran",
        ),
    ]

    projects = [
        Project.objects.create(
            name="Atlas Cultural Center",
            description="A community cultural center with flexible exhibition spaces.",
            client=clients[0],
            start_date=date(2026, 1, 15),
            end_date=date(2026, 10, 30),
            status=Project.Status.IN_PROGRESS,
        ),
        Project.objects.create(
            name="Northline Residence",
            description="A contemporary residential development with shared gardens.",
            client=clients[1],
            start_date=date(2026, 4, 1),
            end_date=date(2027, 2, 28),
            status=Project.Status.PLANNED,
        ),
    ]
    projects[0].architects.set([
        users["amina.architect@example.com"],
        users["youssef.architect@example.com"],
    ])
    projects[1].architects.set([users["amina.architect@example.com"]])

    Task.objects.create(
        title="Develop schematic floor plans",
        description="Prepare the first schematic floor plan options for client review.",
        status=Task.Status.IN_PROGRESS,
        due_date=date(2026, 6, 30),
        project=projects[0],
        architect=users["amina.architect@example.com"],
    )
    Task.objects.create(
        title="Prepare materials concept",
        description="Create a preliminary materials and finishes concept.",
        status=Task.Status.TODO,
        due_date=date(2026, 7, 15),
        project=projects[0],
        architect=users["youssef.architect@example.com"],
    )
    Task.objects.create(
        title="Review site constraints",
        description="Document site constraints and prepare initial design considerations.",
        status=Task.Status.COMPLETED,
        due_date=date(2026, 5, 20),
        project=projects[1],
        architect=users["amina.architect@example.com"],
    )

    return {
        "users": len(users),
        "clients": len(clients),
        "projects": len(projects),
        "tasks": Task.objects.filter(project__in=projects).count(),
    }
