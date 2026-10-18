from django.core.management.base import BaseCommand

from core.seed_data import seed_database


class Command(BaseCommand):
    help = "Create deterministic development users and sample application data."

    def handle(self, *args, **options):
        counts = seed_database()
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded "
                f"{counts['users']} users, "
                f"{counts['clients']} clients, "
                f"{counts['projects']} projects, and "
                f"{counts['tasks']} tasks."
            )
        )
