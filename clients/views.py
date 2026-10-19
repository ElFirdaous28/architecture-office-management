
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from accounts.decorators import role_required
from .forms import ClientForm
from .models import Client


VIEW_ROLES = ("Administrator", "Architect", "Assistant")
ADMIN_ROLE = ("Administrator",)


@role_required(*VIEW_ROLES)
def client_list(request):
    search = request.GET.get("q", "").strip()
    clients = Client.objects.all().order_by("name")
    if search:
        clients = clients.filter(
            models.Q(name__icontains=search)
            | models.Q(email__icontains=search)
            | models.Q(phone__icontains=search)
        )

    page_obj = Paginator(clients, 10).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(request, "clients/list.html", {
        "clients": page_obj,
        "page_obj": page_obj,
        "query_params": query_params.urlencode(),
        "search": search,
    })


@role_required(*ADMIN_ROLE)
def client_create(request):
    form = ClientForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Client created successfully."))
        return redirect("client_list")

    return render(request, "clients/form.html", {
        "form": form,
        "page_title": "Create Client",
    })


@role_required(*ADMIN_ROLE)
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Client updated successfully."))
        return redirect("client_list")

    return render(request, "clients/form.html", {
        "form": form,
        "client": client,
        "page_title": "Edit Client",
    })


@role_required(*ADMIN_ROLE)
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        if client.projects.exists():
            messages.error(
                request,
                _("This client cannot be deleted because they have associated projects."),
            )
        else:
            client.delete()
            messages.success(request, _("Client deleted successfully."))
            return redirect("client_list")

    return render(request, "clients/confirm_delete.html", {
        "client": client,
    })
