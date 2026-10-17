from django.urls import path
from .views import login_view, logout_view, dashboard_view, user_list_view, user_create_view
from .views import RequiredPasswordChangeView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # users management
    path("users/", user_list_view, name="user_list"),
    path("users/create/", user_create_view, name="user_create"),
    path("change-password/",RequiredPasswordChangeView.as_view(),name="password_change"),
]