from django.contrib import admin

from blog.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for the Post model."""

    list_display = ("title", "author", "created_at")
    search_fields = ("title", "content", "author__username", "author__first_name")
    list_filter = ("created_at", "author")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)