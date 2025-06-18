from django.db import models
from django.conf import settings
from django.urls import reverse  # For get_absolute_url
from universities.models import Course
from django.core.exceptions import ValidationError


class DiscussionThread(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="discussion_threads")
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="started_threads",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, help_text="For moderation; soft delete.")

    def __str__(self):
        return f"Thread: {self.title} in {self.course.code}"

    def get_absolute_url(self):
        return reverse("discussions:thread_detail", kwargs={"pk": self.pk})


class Post(models.Model):
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="For nesting replies one level deep",
    )
    is_active = models.BooleanField(default=True, help_text="For moderation; soft delete.")

    def __str__(self):
        author_username = self.author.username if self.author else "Anonymous"
        return f"Post by {author_username} in {self.thread.title}"

    def clean(self):
        super().clean()
        if self.parent:
            # Ensure parent post belongs to the same thread
            if self.parent.thread != self.thread:
                raise ValidationError(
                    {"parent": "The parent post must belong to the same discussion thread."}
                )
            # Ensure nesting is limited to one level (parent cannot be a reply itself)
            if self.parent.parent is not None:
                raise ValidationError(
                    {"parent": "Replies cannot be nested more than one level deep."}
                )

    def get_absolute_url(self):
        # Link to the thread detail page, with an anchor to the post itself
        return (
            f"{reverse('discussions:thread_detail', kwargs={'pk': self.thread.pk})}#post-{self.pk}"
        )

    # Note: For more complex hierarchy management or if performance becomes an issue
    # with deep nesting (even if we're limiting it here), consider packages like
    # django-mptt or django-treebeard. For one-level deep, this is sufficient.
