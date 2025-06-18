from django.urls import path
from .views import UniversityDetailView, FacultyDetailView

app_name = 'universities'

urlpatterns = [
    path('<slug:uni>/', UniversityDetailView.as_view(), name='university_detail'),
    path('<slug:uni>/<slug:faculty>/', FacultyDetailView.as_view(), name='faculty_detail'),
]
