from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.models import User

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "architect"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
                "placeholder": _("Enter task title"),
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
                "rows": 4,
                "placeholder": _("Describe the task"),
            }),
            "due_date": forms.DateInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
                "type": "date",
            }),
            "architect": forms.Select(attrs={"class": "hidden"}),
        }

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["architect"].queryset = project.architects.filter(
            role=User.Role.ARCHITECT,
            is_active=True,
        ).order_by("last_name", "first_name")
        self.fields["architect"].required = True


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={
                "class": "rounded-lg border border-border bg-surface px-3 py-2 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
            }),
        }
