from django import forms

from accounts.models import User
from clients.models import Client

from .models import Project


class ProjectForm(forms.ModelForm):
    architects = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "client",
            "start_date",
            "end_date",
            "status",
            "architects",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/10",
                "placeholder": "Enter project name",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/10",
                "rows": 4,
                "placeholder": "Describe the project",
            }),
            "client": forms.Select(attrs={
                "class": "hidden",
            }),
            "start_date": forms.DateInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
                "type": "date",
            }),
            "end_date": forms.DateInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
                "type": "date",
            }),
            "status": forms.Select(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none focus:border-primary focus:ring-2 focus:ring-primary/10",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.order_by("name")
        self.fields["client"].required = True
        self.fields["client"].empty_label = "Select a client"
        self.fields["architects"].queryset = User.objects.filter(
            role=User.Role.ARCHITECT,
            is_active=True,
        ).order_by("last_name", "first_name")
        self.fields["architects"].label = "Assign architects"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "End date must be on or after the start date.")

        return cleaned_data


class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["status"]