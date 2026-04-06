from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def avatar(user):
    """Render a role-based inline avatar for the given user.

    Displays a crown emoji with purple background for admin users (is_staff),
    and a book emoji with blue background for regular users.

    Usage in templates:
        {% load avatar_tags %}
        {% avatar user %}
    """
    if user.is_staff:
        emoji = "👑"
        bg_classes = "bg-purple-500"
    else:
        emoji = "📖"
        bg_classes = "bg-blue-500"

    return format_html(
        '<span class="inline-flex items-center justify-center w-8 h-8'
        " rounded-full {} text-white text-sm font-bold"
        ' select-none" title="{}">{}</span>',
        bg_classes,
        "Admin" if user.is_staff else "User",
        emoji,
    )