from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    # Ensure profile exists before saving, especially if User was created
    # without the signal firing immediately (e.g. bulk create)
    # or if the profile somehow got deleted.
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance) # Create it if it doesn't exist
    except AttributeError:
        # This can happen if the User instance somehow doesn't have a profile attribute yet
        # though the OneToOneField should create it. This is a safeguard.
        UserProfile.objects.get_or_create(user=instance)
