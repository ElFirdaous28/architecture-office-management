from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from projects.models import Project

from .forms import TaskForm, TaskStatusForm
from .models import Task


def _project_with_tasks(project_pk):
    return get_object_or_404(
        Project.objects.prefetch_related("architects"),
        pk=project_pk,
    )


@role_required("Administrator", "Architect", "Assistant")
def task_list(request, project_pk):
    project = _project_with_tasks(project_pk)
    tasks = project.tasks.select_related("architect").order_by("due_date", "title")
    return render(request, "tasks/list.html", {
        "project": project,
        "tasks": tasks,
        "status_choices": Task.Status.choices,
    })


@role_required("Administrator")
def task_create(request, project_pk):
    project = _project_with_tasks(project_pk)
    form = TaskForm(request.POST or None, project=project)

    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.save()
        messages.success(request, "Task created successfully.")
        return redirect("project_task_list", project_pk=project.pk)

    return render(request, "tasks/form.html", {
        "form": form,
        "project": project,
        "page_title": "Create Task",
    })


@role_required("Administrator")
def task_update(request, project_pk, pk):
    project = _project_with_tasks(project_pk)
    task = get_object_or_404(Task, pk=pk, project=project)
    form = TaskForm(request.POST or None, instance=task, project=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Task updated successfully.")
        return redirect("project_task_list", project_pk=project.pk)

    return render(request, "tasks/form.html", {
        "form": form,
        "project": project,
        "task": task,
        "page_title": "Edit Task",
    })


@login_required
def task_status_update(request, project_pk, pk):
    task = get_object_or_404(
        Task.objects.select_related("project"),
        pk=pk,
        project_id=project_pk,
    )

    if request.method != "POST":
        raise PermissionDenied

    is_admin = request.user.role == "ADMIN"
    is_assigned_architect = (
        request.user.role == "ARCHITECT"
        and task.architect_id == request.user.id
    )
    if not (is_admin or is_assigned_architect):
        raise PermissionDenied

    form = TaskStatusForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, "Task status updated successfully.")
    else:
        messages.error(request, "The task status could not be updated.")

    return redirect("project_task_list", project_pk=project_pk)


@role_required("Administrator")
def task_delete(request, project_pk, pk):
    task = get_object_or_404(Task, pk=pk, project_id=project_pk)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully.")

    return redirect("project_task_list", project_pk=project_pk)

# Create your views here.
