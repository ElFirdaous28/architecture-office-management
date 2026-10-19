from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User


class Command(BaseCommand):
    help = "Permanently delete accounts soft-deleted at least 30 days ago."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=30)
        deleted_count, _ = User.objects.filter(
            deleted_at__isnull=False,
            deleted_at__lte=cutoff,
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Permanently deleted {deleted_count} account(s).")
        )
