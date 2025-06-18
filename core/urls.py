from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing_page"),
    path("search/", views.GlobalSearchView.as_view(), name="global_search"),
    path("moderation/", views.moderation_dashboard, name="moderation_dashboard"),
    path(
        "moderation/toggle/<str:model_name>/<int:object_id>/",
        views.toggle_active_status,
        name="toggle_active_status",
    ),
    path(
        "report/<str:model_name>/<int:object_id>/",
        views.ReportContentView.as_view(),
        name="report_content",
    ),
    path("notifications/", views.NotificationListView.as_view(), name="notification_list"),
]
