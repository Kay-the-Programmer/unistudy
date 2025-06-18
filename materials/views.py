from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.db.models import F, Q # For incrementing download_count and Q objects
from django.http import Http404 # Already imported but good to note

from .models import Material, MaterialTypeChoices # Added MaterialTypeChoices
from universities.models import Course, University # Course model is in universities app, added University
from discussions.models import DiscussionThread # For listing threads on course page
from .forms import MaterialUploadForm

class CourseDetailView(DetailView):
    model = Course
    template_name = 'materials/course_detail.html' # Or 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object

        # Get all active materials for the course initially
        materials_queryset = Material.objects.filter(course=course, is_active=True)

        # Get current filter parameters from GET request
        material_type_param = self.request.GET.get('material_type', '')
        upload_year_param = self.request.GET.get('upload_year', '')
        uploader_university_param = self.request.GET.get('uploader_university', '')

        # Apply filters
        if material_type_param:
            materials_queryset = materials_queryset.filter(material_type=material_type_param)
        if upload_year_param:
            try:
                materials_queryset = materials_queryset.filter(created_at__year=int(upload_year_param))
            except ValueError:
                pass # Ignore invalid year param
        if uploader_university_param:
            try:
                materials_queryset = materials_queryset.filter(uploaded_by__profile__university_id=int(uploader_university_param))
            except ValueError:
                pass # Ignore invalid uni param

        context['materials'] = materials_queryset.order_by('-created_at')
        context['discussion_threads'] = DiscussionThread.objects.filter(course=course, is_active=True).order_by('-created_at')

        # Populate data for filter options
        context['material_type_choices'] = MaterialTypeChoices.choices
        # Get years from all materials of the course, not just filtered ones, for options
        context['upload_year_options'] = Material.objects.filter(course=course, is_active=True).dates('created_at', 'year', order='DESC').distinct()
        context['uploader_university_options'] = University.objects.filter(
            students__user__uploaded_materials__course=course
        ).distinct().order_by('name')

        context['current_filters'] = {
            'material_type': material_type_param,
            'upload_year': upload_year_param,
            'uploader_university': uploader_university_param,
        }
        return context

class MaterialUploadView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialUploadForm
    template_name = 'materials/material_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allowed_extensions'] = MaterialUploadForm.ALLOWED_EXTENSIONS
        context['max_file_size_mb'] = MaterialUploadForm.MAX_FILE_SIZE_MB
        # If course_id is passed in URL query params, pre-select it in the form
        course_id = self.request.GET.get('course_id')
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                # Get the form instance if it's already created by CreateView
                form = context.get('form')
                if form:
                    form.fields['course'].initial = course
            except (Course.DoesNotExist, ValueError):
                pass # Let the form handle invalid or missing course
        return context

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        # The success_url will be to the course page of the uploaded material
        self.success_url = reverse_lazy('materials:course_detail', kwargs={'pk': form.instance.course.pk})
        return super().form_valid(form)

class MaterialDownloadView(LoginRequiredMixin, DetailView):
    model = Material
    # This view does not render a template directly for file serving but might for errors or confirmation.
    # template_name = 'materials/material_download_confirm.html'

    def get(self, request, *args, **kwargs):
        material = self.get_object()

        if not material.is_active and not request.user.is_staff: # Or some other permission check
            raise Http404("Material not found or not available.")

        # Increment download count atomically
        Material.objects.filter(pk=material.pk).update(download_count=F('download_count') + 1)

        # Refresh object from DB to get updated download_count if needed for logging, though not strictly necessary for serving.
        # material.refresh_from_db()

        try:
            # Make sure material.file.path is correct and accessible
            # For cloud storage, material.file.url might be used differently
            return FileResponse(material.file.open('rb'), as_attachment=True, filename=material.file.name.split('/')[-1])
        except FileNotFoundError:
            raise Http404("File not found.")
        except Exception as e:
            # Log the exception e
            # Consider a more user-friendly error page or message
            raise Http404(f"Error serving file: {e}")
