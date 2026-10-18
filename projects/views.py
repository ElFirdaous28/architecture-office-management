from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required

from .forms import ProjectForm
from .models import Project


@role_required("Administrator", "Architect", "Assistant")
def project_list(request):
    projects = Project.objects.select_related("client").prefetch_related(
        "architects"
    ).order_by("-created_at")
    return render(request, "projects/list.html", {"projects": projects})


@role_required("Administrator")
def project_create(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project created successfully.")
        return redirect("project_list")

    return render(request, "projects/form.html", {
        "form": form,
        "page_title": "Create Project",
    })


@role_required("Administrator")
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated successfully.")
        return redirect("project_list")

    return render(request, "projects/form.html", {
        "form": form,
        "project": project,
        "page_title": "Edit Project",
    })


@role_required("Administrator")
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect("project_list")

    return redirect("project_list")
