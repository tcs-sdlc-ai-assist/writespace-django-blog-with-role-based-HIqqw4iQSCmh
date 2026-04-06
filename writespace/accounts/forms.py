from django import forms
from django.contrib.auth.models import User


# Reusable Tailwind CSS classes for form widgets
INPUT_CSS_CLASS = (
    "w-full px-4 py-2 border border-gray-300 rounded-lg"
    " focus:outline-none focus:ring-2 focus:ring-blue-500"
    " focus:border-transparent"
)

SELECT_CSS_CLASS = (
    "w-full px-4 py-2 border border-gray-300 rounded-lg"
    " focus:outline-none focus:ring-2 focus:ring-blue-500"
    " focus:border-transparent bg-white"
)


class LoginForm(forms.Form):
    """Form for user authentication."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter your username",
                "autofocus": True,
            }
        ),
        label="Username",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter your password",
            }
        ),
        label="Password",
    )

    def clean_username(self):
        """Validate that the username is not empty or whitespace-only."""
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("Username cannot be blank.")
        return username

    def clean_password(self):
        """Validate that the password is not empty or whitespace-only."""
        password = self.cleaned_data.get("password", "").strip()
        if not password:
            raise forms.ValidationError("Password cannot be blank.")
        return password


class RegisterForm(forms.Form):
    """Form for new user registration."""

    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Choose a username",
                "autofocus": True,
                "maxlength": "150",
            }
        ),
        label="Username",
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter your first name",
                "maxlength": "150",
            }
        ),
        label="First Name",
    )
    password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter your password",
            }
        ),
        label="Password",
    )
    password2 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Confirm your password",
            }
        ),
        label="Confirm Password",
    )

    def clean_username(self):
        """Validate that the username is not empty and is unique."""
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("Username cannot be blank.")
        if not username.isalnum():
            raise forms.ValidationError(
                "Username must contain only letters and numbers."
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "A user with that username already exists."
            )
        return username

    def clean_first_name(self):
        """Validate that the first name is not empty or whitespace-only."""
        first_name = self.cleaned_data.get("first_name", "").strip()
        if not first_name:
            raise forms.ValidationError("First name cannot be blank.")
        return first_name

    def clean(self):
        """Validate that the two password fields match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data


class CreateUserForm(forms.Form):
    """Form for admin user creation with role selection."""

    ROLE_CHOICES = [
        ("user", "User"),
        ("admin", "Admin"),
    ]

    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter username",
                "maxlength": "150",
            }
        ),
        label="Username",
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter first name",
                "maxlength": "150",
            }
        ),
        label="First Name",
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CSS_CLASS,
                "placeholder": "Enter password",
            }
        ),
        label="Password",
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": SELECT_CSS_CLASS,
            }
        ),
        label="Role",
    )

    def clean_username(self):
        """Validate that the username is not empty and is unique."""
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("Username cannot be blank.")
        if not username.isalnum():
            raise forms.ValidationError(
                "Username must contain only letters and numbers."
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "A user with that username already exists."
            )
        return username

    def clean_first_name(self):
        """Validate that the first name is not empty or whitespace-only."""
        first_name = self.cleaned_data.get("first_name", "").strip()
        if not first_name:
            raise forms.ValidationError("First name cannot be blank.")
        return first_name