# zstudy/api_urls.py
from django.urls import path, include

# STRETCH GOAL: API Endpoints
# Example:
# from rest_framework import routers
# from materials.api_views import MaterialViewSet # Placeholder
#
# router = routers.DefaultRouter()
# router.register(r'materials', MaterialViewSet) # Placeholder

app_name = 'api'

urlpatterns = [
    # path('', include(router.urls)), # Placeholder
    # path('auth/', include('rest_framework.urls', namespace='rest_framework')) # For browsable API login
]
