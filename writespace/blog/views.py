from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from blog.forms import PostForm
from blog.models import Post


def landing_page(request):
    """Public landing page showing the latest 3 blog posts."""
    latest_posts = Post.objects.select_related("author").all()[:3]
    return render(request, "blog/landing_page.html", {"latest_posts": latest_posts})


@login_required
def blog_list(request):
    """Display all blog posts, newest first, for authenticated users."""
    posts = Post.objects.select_related("author").all()
    return render(request, "blog/blog_list.html", {"posts": posts})


@login_required
def blog_detail(request, id):
    """Display a single blog post by UUID."""
    post = get_object_or_404(Post.objects.select_related("author"), id=id)
    is_owner = request.user == post.author
    can_edit = is_owner or request.user.is_staff
    return render(
        request,
        "blog/blog_detail.html",
        {
            "post": post,
            "is_owner": is_owner,
            "can_edit": can_edit,
        },
    )


@login_required
def blog_create(request):
    """Create a new blog post. Sets the author to the current user."""
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog_detail", id=post.id)
    else:
        form = PostForm()
    return render(request, "blog/blog_form.html", {"form": form, "editing": False})


@login_required
def blog_edit(request, id):
    """Edit an existing blog post. Only the author or an admin can edit."""
    post = get_object_or_404(Post.objects.select_related("author"), id=id)
    if request.user != post.author and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog_detail", id=post.id)
    else:
        form = PostForm(instance=post)
    return render(
        request, "blog/blog_form.html", {"form": form, "post": post, "editing": True}
    )


@login_required
def blog_delete(request, id):
    """Delete a blog post. POST only. Only the author or an admin can delete."""
    if request.method != "POST":
        return redirect("blog_list")

    post = get_object_or_404(Post.objects.select_related("author"), id=id)
    if request.user != post.author and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to delete this post.")

    post.delete()
    return redirect("blog_list")