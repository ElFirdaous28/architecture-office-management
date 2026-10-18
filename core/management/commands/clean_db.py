from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.seed_data import clean_database


class Command(BaseCommand):
    help = "Delete application data and reset the database to an empty state."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Skip the confirmation prompt.",
        )

    def handle(self, *args, **options):
        if not options["no_input"]:
            answer = input(
                "This will delete all users, clients, projects, and tasks. "
                "Continue? [y/N] "
            ).strip().lower()
            if answer not in {"y", "yes"}:
                raise CommandError("Database cleanup cancelled.")

        with transaction.atomic():
            clean_database()

        self.stdout.write(self.style.SUCCESS("Application data cleaned."))
