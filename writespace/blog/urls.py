from django.urls import path

from blog.views import (
    blog_create,
    blog_delete,
    blog_detail,
    blog_edit,
    blog_list,
    landing_page,
)

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("blogs/", blog_list, name="blog_list"),
    path("blogs/write/", blog_create, name="blog_create"),
    path("blogs/<uuid:id>/", blog_detail, name="blog_detail"),
    path("blogs/<uuid:id>/edit/", blog_edit, name="blog_edit"),
    path("blogs/<uuid:id>/delete/", blog_delete, name="blog_delete"),
]