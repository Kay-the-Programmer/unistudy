from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm as DjangoUserCreationForm,
)
from django.contrib.auth.models import User
from django.utils.text import slugify
import random
import string


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))


class UserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    first_name = forms.CharField(required=False, label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")  # Username will be derived

    def save(self, commit=True):
        user = super().save(commit=False)
        # Auto-generate username from email if not provided or make it unique
        # For simplicity, we'll use the email prefix and add random chars if needed
        # This is a basic approach; a more robust username generation might be needed
        if not user.username:
            email_prefix = slugify(self.cleaned_data["email"].split("@")[0])
            # Ensure username is unique
            username_candidate = email_prefix
            while User.objects.filter(username=username_candidate).exists():
                random_suffix = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=4)
                )
                username_candidate = f"{email_prefix}_{random_suffix}"
            user.username = username_candidate

        if commit:
            user.save()
        return user


# Note: To use these forms, you'll need to create views that utilize them.
# The LOGIN_URL in settings.py will point to a view that uses EmailAuthenticationForm.
# A new signup view will use UserCreationForm.
