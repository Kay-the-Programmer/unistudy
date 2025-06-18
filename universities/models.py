from django.db import models
from django.utils.text import slugify
from django.db.models import UniqueConstraint


class University(models.Model):
    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=200, unique=True, help_text="URL-friendly version of the name"
    )
    logo = models.ImageField(upload_to="university_logos/", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Faculty(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="faculties")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, help_text="URL-friendly version of the name")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["university", "slug"], name="unique_faculty_slug_per_university"
            ),
            UniqueConstraint(
                fields=["university", "name"], name="unique_faculty_name_per_university"
            ),
        ]

    def __str__(self):
        return f"{self.name}, {self.university.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="courses")
    code = models.CharField(max_length=20, help_text="e.g. CS101")
    title = models.CharField(max_length=200)
    year_offered = models.PositiveIntegerField(
        help_text="Year the course is typically offered, e.g., 1, 2, 3, 4"
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=["faculty", "code"], name="unique_course_code_per_faculty"),
            UniqueConstraint(fields=["faculty", "title"], name="unique_course_title_per_faculty"),
        ]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.title} ({self.faculty.name})"
