from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from accounts.forms import CreateUserForm, LoginForm, RegisterForm
from blog.models import Post


def staff_required(user):
    """Check that the user is an active staff member (admin)."""
    return user.is_staff


def login_view(request):
    """Authenticate a user and redirect based on role.

    GET: Display the login form.
    POST: Validate credentials, log in, and redirect.
        - Admin users are redirected to the admin dashboard.
        - Regular users are redirected to the blog list.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_dashboard")
        return redirect("blog_list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect("admin_dashboard")
                return redirect("blog_list")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    """Register a new regular user, log them in, and redirect to blog list.

    GET: Display the registration form.
    POST: Validate input, create user, auto-login, and redirect.
    """
    if request.user.is_authenticated:
        return redirect("blog_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["first_name"],
            )
            login(request, user)
            return redirect("blog_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def logout_view(request):
    """Log out the current user and redirect to the landing page.

    Only accepts POST requests for CSRF safety.
    """
    if request.method == "POST":
        logout(request)
        return redirect("landing_page")
    return redirect("landing_page")


@login_required
@user_passes_test(staff_required)
def admin_dashboard(request):
    """Display the admin dashboard with platform statistics.

    Stats include total users, total admins, total posts,
    and the 5 most recent posts.
    """
    total_users = User.objects.count()
    total_admins = User.objects.filter(is_staff=True).count()
    total_posts = Post.objects.count()
    recent_posts = Post.objects.select_related("author").all()[:5]

    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_posts": total_posts,
            "recent_posts": recent_posts,
        },
    )


@login_required
@user_passes_test(staff_required)
def user_management(request):
    """Display the user management page with all users and a creation form.

    Lists all users and provides a form for creating new users.
    """
    users = User.objects.all().order_by("-date_joined")
    form = CreateUserForm()

    return render(
        request,
        "accounts/user_management.html",
        {
            "users": users,
            "form": form,
        },
    )


@login_required
@user_passes_test(staff_required)
def user_create(request):
    """Create a new user with the specified role. POST only.

    Admins can create users with either 'user' or 'admin' role.
    Redirects back to user management on success or failure.
    """
    if request.method != "POST":
        return redirect("user_management")

    form = CreateUserForm(request.POST)
    if form.is_valid():
        role = form.cleaned_data["role"]
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
            first_name=form.cleaned_data["first_name"],
        )
        if role == "admin":
            user.is_staff = True
            user.save()
        return redirect("user_management")

    # If form is invalid, re-render user management with errors
    users = User.objects.all().order_by("-date_joined")
    return render(
        request,
        "accounts/user_management.html",
        {
            "users": users,
            "form": form,
        },
    )


@login_required
@user_passes_test(staff_required)
def user_delete(request, id):
    """Delete a user by ID. POST only.

    Prevents admins from deleting themselves or the default admin
    (username 'admin'). Returns 403 for forbidden operations.
    """
    if request.method != "POST":
        return redirect("user_management")

    try:
        user_to_delete = User.objects.get(id=id)
    except User.DoesNotExist:
        return redirect("user_management")

    # Prevent self-deletion
    if user_to_delete == request.user:
        return HttpResponseForbidden("You cannot delete your own account.")

    # Prevent deletion of the default admin user
    if user_to_delete.username == "admin":
        return HttpResponseForbidden("The default admin account cannot be deleted.")

    user_to_delete.delete()
    return redirect("user_management")