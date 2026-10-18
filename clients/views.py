
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from .forms import ClientForm
from .models import Client


VIEW_ROLES = ("Administrator", "Architect", "Assistant")
ADMIN_ROLE = ("Administrator",)


@role_required(*VIEW_ROLES)
def client_list(request):
    clients = Client.objects.all().order_by("name")
    return render(request, "clients/list.html", {"clients": clients})


@role_required(*ADMIN_ROLE)
def client_create(request):
    form = ClientForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Client created successfully.")
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
        messages.success(request, "Client updated successfully.")
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
                "This client cannot be deleted because they have associated projects.",
            )
        else:
            client.delete()
            messages.success(request, "Client deleted successfully.")
            return redirect("client_list")

    return render(request, "clients/confirm_delete.html", {
        "client": client,
    })
