from django.db import models
from django.conf import settings
from django.urls import reverse  # For get_absolute_url
from universities.models import Course
from taggit.managers import TaggableManager


class MaterialTypeChoices(models.TextChoices):
    PAST_PAPER = "PAST_PAPER", "Past Paper"
    NOTES = "NOTES", "Lecture Notes"
    ASSIGNMENT = "ASSIGNMENT", "Assignment"
    OTHER = "OTHER", "Other"


class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_materials",
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="materials/%Y/%m/%d/")
    material_type = models.CharField(
        max_length=20, choices=MaterialTypeChoices.choices, default=MaterialTypeChoices.OTHER
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    tags = TaggableManager(blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="For moderation; soft delete.")

    class Meta:
        indexes = [
            models.Index(fields=["course", "material_type"]),
        ]

    def __str__(self):
        return f"{self.title} for {self.course.code}"

    def get_absolute_url(self):
        # Point to material on course page
        course_url = reverse("materials:course_detail", kwargs={"pk": self.course.pk})
        return f"{course_url}#material-{self.pk}"

# STRETCH GOAL: Bookmark/Save-for-Offline
# class UserMaterialBookmark(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     material = models.ForeignKey(Material, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         unique_together = ('user', 'material')
