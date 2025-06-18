from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Material
from universities.models import Course  # To use ModelChoiceField for course selection
import os


class MaterialUploadForm(forms.ModelForm):
    ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "ppt", "pptx", "zip"]
    MAX_FILE_SIZE_MB = 20
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related("faculty", "faculty__university").all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select the course this material belongs to.",
    )

    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text=(
            f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}. " f"Max size: {MAX_FILE_SIZE_MB}MB."
        ),  # Reformatted help_text
    )

    class Meta:
        model = Material
        fields = ["title", "course", "material_type", "file", "description", "tags"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter material title (or leave blank to use filename)"}
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "tags": "Enter comma-separated tags (e.g., exam, notes, chapter1).",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uploaded_filename = None
        self.fields["course"].label_from_instance = lambda obj: (
            f"{obj.code} - {obj.title} ({obj.faculty.name}, " f"{obj.faculty.university.name})"
        )  # Reformatted lambda
        self.fields["title"].required = False

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            self.uploaded_filename = file.name
            if file.size > self.MAX_FILE_SIZE_BYTES:
                current_size_mb = file.size // (1024 * 1024)
                raise ValidationError(
                    f"File size ({current_size_mb}MB) exceeds the "
                    f"maximum limit of {self.MAX_FILE_SIZE_MB}MB."
                )  # Reformatted error
        return file

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title and self.uploaded_filename:
            filename_without_extension, _ = os.path.splitext(self.uploaded_filename)
            title = filename_without_extension.replace("_", " ").replace("-", " ").capitalize()

        if not title:
            raise ValidationError(
                "Title is required. If blank, filename must be provided for auto-title."
            )  # Reformatted error
        return title
