"""
URL configuration for zstudy project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Accounts app for login, signup, logout
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # Universities app (e.g., /u/cambridge/)
    path("u/", include("universities.urls", namespace="universities")),
    # Materials app (e.g., /materials/course/<pk>/, /materials/material/upload/)
    path("materials/", include("materials.urls", namespace="materials")),
    # Discussions app (e.g., /discussions/thread/<pk>/)
    path("discussions/", include("discussions.urls", namespace="discussions")),
    # API URLs
    path("api/", include("zstudy.api_urls", namespace="api")),
    # Core app (landing page at root, notifications at /notifications/, moderation at /moderation/)
    path("", include("core.urls", namespace="core")),
]

# Serve static and media files during development
if settings.DEBUG:
    # Serve static files (collected by collectstatic)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve user-uploaded media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
