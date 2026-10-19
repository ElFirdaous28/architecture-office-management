from django.urls import path
from .views import (
    login_view,
    logout_view,
    dashboard_view,
    profile_view,
    required_password_change_view,
    user_list_view,
    user_create_view,
    user_delete_view,
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path("profile/", profile_view, name="profile"),

    # users management
    path("users/", user_list_view, name="user_list"),
    path("users/create/", user_create_view, name="user_create"),
    path("users/<int:pk>/delete/", user_delete_view, name="user_delete"),
    path("change-password/", required_password_change_view, name="password_change"),
    path("password/", profile_view, name="password_update"),
]