from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Material
from universities.models import Course # To use ModelChoiceField for course selection
import os

class MaterialUploadForm(forms.ModelForm):
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip']
    MAX_FILE_SIZE_MB = 20
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related('faculty', 'faculty__university').all(),
        widget=forms.Select(attrs={'class': 'form-control'}), # Class for styling if needed
        help_text="Select the course this material belongs to."
    )

    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text=f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}. Max size: {MAX_FILE_SIZE_MB}MB."
    )

    class Meta:
        model = Material
        fields = ['title', 'course', 'material_type', 'file', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter material title (or leave blank to use filename)'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'tags': 'Enter comma-separated tags (e.g., exam, notes, chapter1).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uploaded_filename = None # To store filename for title auto-population
        self.fields['course'].label_from_instance = lambda obj: f"{obj.code} - {obj.title} ({obj.faculty.name}, {obj.faculty.university.name})"
        # Make title not strictly required at the form field level, will handle in clean_title
        self.fields['title'].required = False


    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Store filename for title auto-population
            self.uploaded_filename = file.name

            # File size validation
            if file.size > self.MAX_FILE_SIZE_BYTES:
                raise ValidationError(
                    f"File size exceeds the maximum limit of {self.MAX_FILE_SIZE_MB}MB. "
                    f"Current file size: {file.size // (1024 * 1024)}MB."
                )
        # If file is not provided (e.g. on form edit where file is already set),
        # this clean method might not be what we want if we allow clearing the file.
        # For create view, file is required. For update, it's not.
        # The `forms.FileField` already handles `required=True` by default.
        # If we make it not required for updates, this logic needs adjustment.
        # For now, assuming it's for create or always requires a file on update.
        return file

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title and self.uploaded_filename:
            # Auto-populate title from filename if title is empty
            filename_without_extension, _ = os.path.splitext(self.uploaded_filename)
            # Basic sanitization: replace underscores/hyphens with spaces, capitalize
            title = filename_without_extension.replace('_', ' ').replace('-', ' ').capitalize()

        if not title: # If still no title (e.g. no file uploaded yet or filename was just an extension)
            raise ValidationError("Title is required. If you leave it blank, a filename must be provided to auto-generate the title.")
        return title
