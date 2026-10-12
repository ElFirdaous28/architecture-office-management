
from django.db import migrations


ROLE_GROUPS = {
    "ADMIN": "Administrator",
    "ARCHITECT": "Architect",
    "ASSISTANT": "Assistant",
}

MODEL_PERMISSIONS = {
    "Administrator": {
        "accounts.User": ("add", "view", "change", "delete"),
        "clients.Client": ("add", "view", "change", "delete"),
        "projects.Project": ("add", "view", "change", "delete"),
        "tasks.Task": ("add", "view", "change", "delete"),
    },
    "Architect": {
        "projects.Project": ("view", "change"),
        "tasks.Task": ("view", "change"),
    },
    "Assistant": {
        "clients.Client": ("view",),
        "projects.Project": ("view",),
        "tasks.Task": ("view",),
    },
}


def setup_role_groups(apps, schema_editor):
    db = schema_editor.connection.alias

    User = apps.get_model("accounts", "User")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    groups = {}

    # Create the three application roles.
    for group_name in ROLE_GROUPS.values():
        group, _ = Group.objects.using(db).get_or_create(
            name=group_name
        )
        groups[group_name] = group

    # Create or retrieve the model permissions and assign them.
    for group_name, models_permissions in MODEL_PERMISSIONS.items():
        group = groups[group_name]

        for model_label, actions in models_permissions.items():
            app_label, model_name = model_label.split(".")

            content_type, _ = ContentType.objects.db_manager(db).get_or_create(
                app_label=app_label,
                model=model_name.lower(),
            )

            for action in actions:
                codename = f"{action}_{model_name.lower()}"

                permission, _ = Permission.objects.using(db).get_or_create(
                    content_type=content_type,
                    codename=codename,
                    defaults={
                        "name": f"Can {action} {model_name.lower()}",
                    },
                )

                group.permissions.add(permission)

    # Preserve existing users and map their current roles to Groups.
    for user in User.objects.using(db).all().iterator():
        group_name = ROLE_GROUPS.get(user.role)

        if group_name:
            user.groups.add(groups[group_name])


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounts",
            "0002_alter_user_managers_remove_user_name_and_more",
        ),
        ("clients", "0001_initial"),
        ("projects", "0001_initial"),
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(setup_role_groups, migrations.RunPython.noop),
    ]
