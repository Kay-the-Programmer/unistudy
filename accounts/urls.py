from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignupView
from .forms import EmailAuthenticationForm # Custom form for login

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=EmailAuthenticationForm
        ),
        name='login'
    ),
    path(
        'logout/',
        # Assuming core app will have a 'landing_page' defined
        # If not, LOGOUT_REDIRECT_URL from settings will be used.
        auth_views.LogoutView.as_view(next_page=reverse_lazy('core:landing_page')),
        name='logout'
    ),
]
