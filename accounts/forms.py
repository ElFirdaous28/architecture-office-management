
import secrets

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User


class UserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[
            ("Administrator", _("Administrator")),
            ("Architect", _("Architect")),
            ("Assistant", _("Assistant")),
        ]
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)

        self.generated_password = secrets.token_urlsafe(16)
        user.set_password(self.generated_password)

        role_group = self.cleaned_data["role"]
        user.role = {
            "Administrator": User.Role.ADMIN,
            "Architect": User.Role.ARCHITECT,
            "Assistant": User.Role.ASSISTANT,
        }[role_group]
        user.must_change_password = True

        if commit:
            user.save()
            user.groups.set([Group.objects.get(name=role_group)])

        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

class RequiredPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1")

        if new_password and self.user.check_password(new_password):
            raise forms.ValidationError(
                _("Your new password must be different from your current password.")
            )

        return new_password