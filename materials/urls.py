from django.urls import path
from .views import CourseDetailView, MaterialUploadView, MaterialDownloadView

app_name = 'materials'

urlpatterns = [
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('material/upload/', MaterialUploadView.as_view(), name='material_upload'),
    path('material/<int:pk>/download/', MaterialDownloadView.as_view(), name='material_download'),
]
