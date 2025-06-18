from django.db import models
from django.contrib.auth.models import User
from universities.models import University # Assuming University model is in 'universities' app

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        db_index=True  # Added db_index as suggested
    )
    programme = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., Bachelor of Science in Computer Science"
    )
    year_of_study = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="e.g., 1, 2, 3, 4, 5"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default_avatar.png',
        blank=True,
        null=True
    )
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
