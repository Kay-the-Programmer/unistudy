from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import UserCreationForm # Using the custom one

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login') # Redirect to login after successful signup

    def form_valid(self, form):
        # This is where an email verification hook would be triggered.
        # For example:
        # user = form.save()
        # send_verification_email(user) # Placeholder for actual email sending logic
        # messages.info(self.request, "Please check your email to verify your account.")
        # For now, just save the user.
        return super().form_valid(form)

# LoginView and LogoutView are Django's built-in views.
# They will be configured in accounts/urls.py.
