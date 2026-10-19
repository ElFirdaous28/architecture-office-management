from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from accounts.decorators import role_required

from .forms import ProjectForm, ProjectStatusForm
from .models import Project


@role_required("Administrator", "Architect", "Assistant")
def project_list(request):
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    projects = Project.objects.select_related("client").prefetch_related(
        "architects"
    ).order_by("-created_at")
    if request.user.role == "ARCHITECT":
        projects = projects.filter(architects=request.user)
    if search:
        projects = projects.filter(
            models.Q(name__icontains=search)
            | models.Q(description__icontains=search)
            | models.Q(client__name__icontains=search)
        )
    if status in dict(Project.Status.choices):
        projects = projects.filter(status=status)

    page_obj = Paginator(projects, 10).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(request, "projects/list.html", {
        "projects": page_obj,
        "page_obj": page_obj,
        "query_params": query_params.urlencode(),
        "search": search,
        "status": status,
        "project_status_choices": Project.Status.choices,
    })


@role_required("Administrator")
def project_create(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Project created successfully."))
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
        messages.success(request, _("Project updated successfully."))
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
        messages.success(request, _("Project deleted successfully."))
        return redirect("project_list")

    return redirect("project_list")


@role_required("Administrator")
def project_status_update(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method != "POST":
        return redirect("project_list")

    form = ProjectStatusForm(request.POST, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, _("Project status updated successfully."))
    else:
        messages.error(request, _("The project status could not be updated."))

    return redirect("project_list")
