from django.urls import path

from accounts.views import (
    admin_dashboard,
    login_view,
    logout_view,
    register_view,
    user_create,
    user_delete,
    user_management,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin/users/", user_management, name="user_management"),
    path("admin/users/create/", user_create, name="user_create"),
    path("admin/users/<int:id>/delete/", user_delete, name="user_delete"),
]