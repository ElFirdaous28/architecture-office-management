
from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "phone", "address"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/10",
                "placeholder": "Enter client name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/10",
                "placeholder": "client@example.com",
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/10",
                "placeholder": "Enter phone number",
            }),
            "address": forms.TextInput(attrs={
                "class": "w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-neutral outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/10",
                "placeholder": "Enter client address",
            }),
        }
