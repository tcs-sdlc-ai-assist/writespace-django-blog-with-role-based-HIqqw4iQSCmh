from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Unregister the default User admin and re-register with customized display
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Customized admin configuration for the User model.

    Extends Django's built-in UserAdmin with additional list display
    fields and filters relevant to the WriteSpace platform.
    """

    list_display = (
        "username",
        "first_name",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "first_name", "email")
    list_filter = ("is_staff", "is_active", "date_joined")
    ordering = ("-date_joined",)