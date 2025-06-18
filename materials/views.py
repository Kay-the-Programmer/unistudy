from django.urls import reverse_lazy  # Keep for get_success_url
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.db.models import F
from django.contrib.auth import get_user_model

from .models import Material, MaterialTypeChoices
from universities.models import Course, University
from discussions.models import DiscussionThread
from .forms import MaterialUploadForm
from core.notifications import create_bulk_notifications

User = get_user_model()


class CourseDetailView(DetailView):
    model = Course
    template_name = "materials/course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        materials_queryset = Material.objects.filter(course=course, is_active=True)

        material_type_param = self.request.GET.get("material_type", "")
        upload_year_param = self.request.GET.get("upload_year", "")
        uploader_university_param = self.request.GET.get("uploader_university", "")

        if material_type_param:
            materials_queryset = materials_queryset.filter(material_type=material_type_param)
        if upload_year_param:
            try:
                materials_queryset = materials_queryset.filter(
                    created_at__year=int(upload_year_param)
                )
            except ValueError:
                pass
        if uploader_university_param:
            try:
                materials_queryset = materials_queryset.filter(
                    uploaded_by__profile__university_id=int(uploader_university_param)
                )
            except ValueError:
                pass

        context["materials"] = materials_queryset.order_by("-created_at")
        context["discussion_threads"] = DiscussionThread.objects.filter(
            course=course, is_active=True
        ).order_by("-created_at")

        context["material_type_choices"] = MaterialTypeChoices.choices
        context["upload_year_options"] = (
            Material.objects.filter(course=course, is_active=True)
            .dates("created_at", "year", order="DESC")
            .distinct()
        )
        context["uploader_university_options"] = (
            University.objects.filter(students__user__uploaded_materials__course=course)
            .distinct()
            .order_by("name")
        )
        context["current_filters"] = {
            "material_type": material_type_param,
            "upload_year": upload_year_param,
            "uploader_university": uploader_university_param,
        }
        return context


class MaterialUploadView(LoginRequiredMixin, CreateView):
    model = Material
    form_class = MaterialUploadForm
    template_name = "materials/material_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allowed_extensions"] = MaterialUploadForm.ALLOWED_EXTENSIONS
        context["max_file_size_mb"] = MaterialUploadForm.MAX_FILE_SIZE_MB
        course_id = self.request.GET.get("course_id")
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                form = context.get("form")
                if form:
                    form.fields["course"].initial = course
            except (Course.DoesNotExist, ValueError):
                pass
        return context

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)  # self.object is set here

        material = self.object
        course = material.course
        uploader = self.request.user
        verb = f"New material '{material.title}' was uploaded to {course.code} ({course.title})"
        if course.faculty and course.faculty.university:
            recipients_qs = User.objects.filter(
                profile__university=course.faculty.university
            ).exclude(pk=uploader.pk)
            create_bulk_notifications(
                recipient_qs=recipients_qs,
                verb=verb,
                action_object=material,
                target=course,
                actor=uploader,
            )
        return response

    def get_success_url(self):  # Added for CreateView
        return reverse_lazy("materials:course_detail", kwargs={"pk": self.object.course.pk})


class MaterialDownloadView(LoginRequiredMixin, DetailView):
    model = Material

    def get(self, request, *args, **kwargs):
        material = self.get_object()
        if not material.is_active and not request.user.is_staff:
            raise Http404("Material not found or not available.")
        Material.objects.filter(pk=material.pk).update(download_count=F("download_count") + 1)
        try:
            return FileResponse(
                material.file.open("rb"),
                as_attachment=True,
                filename=material.file.name.split("/")[-1],
            )
        except FileNotFoundError:
            raise Http404("File not found.")
        except Exception as e:
            raise Http404(f"Error serving file: {e}")
