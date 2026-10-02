from django.conf import settings
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    name = models.CharField(max_length=150)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )
    architect = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )

    def __str__(self):
        return self.name