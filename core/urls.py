from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing_page'),
    path('search/', views.GlobalSearchView.as_view(), name='global_search'),
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
]
