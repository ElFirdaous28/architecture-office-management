from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from clients.models import Client
from projects.models import Project
from tasks.models import Task

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(
            request,
            'accounts/login.html',
            {'error': 'Invalid email or password.'}
        )

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    groups = set(user.groups.values_list('name', flat=True))

    context = {
        'total_clients': Client.objects.count(),
        'total_projects': Project.objects.count(),
        'total_tasks': Task.objects.count(),
        'completed_projects': Project.objects.filter(
            status=Project.Status.COMPLETED
        ).count(),
        'completed_tasks': Task.objects.filter(
            status=Task.Status.COMPLETED
        ).count(),
        'user_role': next(
            (
                name
                for name in ('Administrator', 'Architect', 'Assistant')
                if name in groups
            ),
            'No role assigned',
        ),
        'is_administrator': 'Administrator' in groups,
        'is_architect': 'Architect' in groups,
        'is_assistant': 'Assistant' in groups,
    }

    if 'Architect' in groups:
        context['my_projects'] = Project.objects.filter(
            architect=user
        )
        context['my_tasks'] = Task.objects.filter(
            architect=user
        )

    if 'Administrator' in groups:
        template_name = 'accounts/dashboards/administrator.html'
    elif 'Architect' in groups:
        template_name = 'accounts/dashboards/architect.html'
    elif 'Assistant' in groups:
        template_name = 'accounts/dashboards/assistant.html'
    else:
        raise PermissionDenied

    return render(request, template_name, context)