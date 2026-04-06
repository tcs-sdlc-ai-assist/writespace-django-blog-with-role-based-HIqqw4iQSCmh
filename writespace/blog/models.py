import uuid

from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    """Blog post model with UUID primary key and author relationship."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return self.title