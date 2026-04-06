from django import forms

from blog.models import Post


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""

    class Meta:
        model = Post
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-4 py-2 border border-gray-300 rounded-lg"
                        " focus:outline-none focus:ring-2 focus:ring-blue-500"
                        " focus:border-transparent"
                    ),
                    "placeholder": "Enter your post title",
                    "maxlength": "200",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": (
                        "w-full px-4 py-2 border border-gray-300 rounded-lg"
                        " focus:outline-none focus:ring-2 focus:ring-blue-500"
                        " focus:border-transparent"
                    ),
                    "placeholder": "Write your post content here...",
                    "rows": 10,
                }
            ),
        }
        labels = {
            "title": "Title",
            "content": "Content",
        }

    def clean_title(self):
        """Validate that the title is not empty or whitespace-only."""
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Title cannot be blank.")
        return title

    def clean_content(self):
        """Validate that the content is not empty or whitespace-only."""
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise forms.ValidationError("Content cannot be blank.")
        return content