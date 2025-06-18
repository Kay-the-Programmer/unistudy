from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from .models import University, Faculty, Course

class UniversityDetailView(DetailView):
    model = University
    template_name = 'universities/university_detail.html'
    slug_url_kwarg = 'uni' # The name of the slug parameter in the URL
    slug_field = 'slug'    # The field on the University model to match against
    context_object_name = 'university'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The University object is already in context as 'university'
        # Add list of its faculties
        context['faculties'] = self.object.faculties.all()
        return context

class FacultyDetailView(DetailView):
    model = Faculty
    template_name = 'universities/faculty_detail.html'
    context_object_name = 'faculty'
    # We need to look up by both university slug and faculty slug

    def get_object(self, queryset=None):
        # Get the university first
        uni_slug = self.kwargs.get('uni')
        faculty_slug = self.kwargs.get('faculty')

        if uni_slug is None or faculty_slug is None:
            # This case should ideally be caught by URL pattern validation
            # or raise Http404 earlier.
            raise Http404("University or Faculty slug not provided in URL.")

        # Ensure the university exists
        university = get_object_or_404(University, slug=uni_slug)

        # Now get the faculty belonging to this university
        faculty = get_object_or_404(Faculty, university=university, slug=faculty_slug)
        return faculty

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The Faculty object is already in context as 'faculty'
        # Add list of its courses
        context['courses'] = self.object.courses.all()
        return context
