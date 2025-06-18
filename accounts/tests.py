from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings # To check MEDIA_URL for default avatar
import os # For checking default avatar path

from .models import UserProfile
from universities.models import University # Assuming University model is in 'universities' app

User = get_user_model()

class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser1", email="test1@example.com", password="password123")
        # UserProfile should be created by signal
        self.university = University.objects.create(name="Test University for Profile", city="Profileville")

    def test_user_profile_created_signal(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
        self.assertEqual(self.user.profile.user, self.user)

    def test_user_profile_str(self):
        self.assertEqual(str(self.user.profile), f"{self.user.username}'s Profile")

    def test_user_profile_defaults(self):
        profile = self.user.profile
        self.assertFalse(profile.email_verified)
        self.assertEqual(profile.programme, "")
        self.assertIsNone(profile.year_of_study)
        self.assertIsNone(profile.university) # Initially no university

        # Check default avatar path
        # The default='avatars/default_avatar.png' in ImageField refers to the path within MEDIA_ROOT
        # The .url attribute will prepend MEDIA_URL
        # Ensure MEDIA_URL is configured in settings for this test to be robust, or check field.default
        expected_default_avatar_path = 'avatars/default_avatar.png'
        self.assertEqual(profile.avatar.field.default, expected_default_avatar_path)

        # If MEDIA_URL is '/', then profile.avatar.url should be '/avatars/default_avatar.png'
        # If MEDIA_URL is '/media/', then profile.avatar.url should be '/media/avatars/default_avatar.png'
        # For testing the default value itself without relying on storage/MEDIA_URL:
        # Create a new user and check profile.avatar *before* saving the profile again if signal saves it.
        new_user = User.objects.create_user(username="newuser", password="password")
        # The signal creates the profile. If the signal calls .save() on profile,
        # and if ImageField has upload_to, it might alter the path.
        # However, for a default value, it should remain as specified.
        self.assertEqual(new_user.profile.avatar.name, expected_default_avatar_path)


    def test_user_profile_can_link_university(self):
        profile = self.user.profile
        profile.university = self.university
        profile.programme = "BSc Computer Science"
        profile.year_of_study = 2
        profile.email_verified = True
        profile.save()

        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.university, self.university)
        self.assertEqual(updated_profile.programme, "BSc Computer Science")
        self.assertEqual(updated_profile.year_of_study, 2)
        self.assertTrue(updated_profile.email_verified)

    def test_user_profile_avatar_default_path_on_instance(self):
        # This test checks the actual field value on an instance when no avatar is uploaded
        # If an avatar is uploaded, profile.avatar.name would be different.
        profile = self.user.profile
        # When no file is uploaded, and a default is set, the field's value should be the default path.
        self.assertEqual(profile.avatar.name, 'avatars/default_avatar.png')

        # To check the URL, you'd need MEDIA_URL setting
        # Assuming MEDIA_URL = "/media/"
        # expected_url = settings.MEDIA_URL + 'avatars/default_avatar.png'
        # self.assertEqual(profile.avatar.url, expected_url)
        # This part is environment dependent, so testing .name for default is more robust for unit tests.

    # Test that deleting User also deletes UserProfile due to on_delete=models.CASCADE
    def test_user_profile_deleted_with_user(self):
        user_pk = self.user.pk
        self.user.delete()
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(user_id=user_pk)
