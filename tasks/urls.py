from django.urls import path

from . import views

urlpatterns = [
    path(
        "projects/<int:project_pk>/tasks/",
        views.task_list,
        name="project_task_list",
    ),
    path(
        "projects/<int:project_pk>/tasks/create/",
        views.task_create,
        name="task_create",
    ),
    path(
        "projects/<int:project_pk>/tasks/<int:pk>/edit/",
        views.task_update,
        name="task_update",
    ),
    path(
        "projects/<int:project_pk>/tasks/<int:pk>/status/",
        views.task_status_update,
        name="task_status_update",
    ),
    path(
        "projects/<int:project_pk>/tasks/<int:pk>/delete/",
        views.task_delete,
        name="task_delete",
    ),
]
