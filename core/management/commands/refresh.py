from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.seed_data import clean_database, seed_database


class Command(BaseCommand):
    help = "Clean application data and seed fresh development data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Skip the confirmation prompt.",
        )

    def handle(self, *args, **options):
        if not options["no_input"]:
            answer = input(
                "This will delete all application data and create fresh seed data. "
                "Continue? [y/N] "
            ).strip().lower()
            if answer not in {"y", "yes"}:
                raise CommandError("Database refresh cancelled.")

        with transaction.atomic():
            clean_database()
            counts = seed_database()

        self.stdout.write(
            self.style.SUCCESS(
                "Database refreshed with "
                f"{counts['users']} users, "
                f"{counts['clients']} clients, "
                f"{counts['projects']} projects, and "
                f"{counts['tasks']} tasks."
            )
        )
