from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

from core.models import Notification # Use direct import
from materials.models import Material # Example target/action_object
from universities.models import University, Faculty, Course # For creating Material

User = get_user_model()

class NotificationModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.recipient_user = User.objects.create_user(username="recipient_user", password="password123")
        cls.actor_user = User.objects.create_user(username="actor_user", password="password123")

        # Setup for creating a Material instance
        cls.university = University.objects.create(name="Core Test University", city="Coreville")
        cls.faculty = Faculty.objects.create(university=cls.university, name="Core Test Faculty")
        cls.course = Course.objects.create(faculty=cls.faculty, code="CT101", title="Core Testing 101", year_offered=1)

        # Example action_object (e.g., the user who performed an action, or the object created)
        # For simplicity, let's use the actor_user's profile if available, or actor_user.
        # Note: UserProfile is created by a signal.
        cls.action_object_actor = cls.actor_user
        if hasattr(cls.actor_user, 'profile'):
            cls.action_object_actor = cls.actor_user.profile

        # Example target_object (e.g., the course a material was uploaded to)
        cls.target_object_course = cls.course

        # Example specific object like a Material (could be action_object or target depending on notification verb)
        from django.core.files.uploadedfile import SimpleUploadedFile
        dummy_file = SimpleUploadedFile("core_test_material.txt", b"content", content_type="text/plain")
        cls.material_object = Material.objects.create(
            course=cls.course,
            uploaded_by=cls.actor_user,
            title="Core Test Material",
            file=dummy_file
        )

    def test_create_notification_with_target(self):
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb="A new material was added to a course you follow.",
            target=self.target_object_course
        )
        self.assertEqual(notification.recipient, self.recipient_user)
        self.assertEqual(notification.verb, "A new material was added to a course you follow.")
        self.assertEqual(notification.target, self.target_object_course)
        self.assertIsNone(notification.action_object)
        self.assertEqual(str(notification), f"Notification for {self.recipient_user.username}: A new material was added to a course you follow. (Read: False)")

    def test_create_notification_with_action_object(self):
        # Here, action_object is the User (actor_user) who performed an action
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb=f"{self.actor_user.username} started following you.",
            action_object=self.action_object_actor
        )
        self.assertEqual(notification.action_object, self.action_object_actor)
        self.assertIsNone(notification.target)

    def test_create_notification_with_both_gfk(self):
        # Example: actor_user (action_object_actor) commented on material_object (target)
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb=f"{self.actor_user.username} commented on your material '{self.material_object.title}'.",
            action_object=self.action_object_actor, # The user who commented
            target=self.material_object # The material that was commented on
        )
        self.assertEqual(notification.action_object, self.action_object_actor)
        self.assertEqual(notification.target, self.material_object)

    def test_notification_defaults(self):
        notification = Notification.objects.create(recipient=self.recipient_user, verb="Test verb.")
        self.assertFalse(notification.is_read) # Default is_read
        self.assertIsNotNone(notification.created_at) # Should be set automatically

    def test_notification_ordering(self):
        # Create three notifications with slightly different times
        n1 = Notification.objects.create(recipient=self.recipient_user, verb="First notification.")
        # Ensure created_at is distinct for ordering test
        n1.created_at = timezone.now() - timedelta(minutes=2)
        n1.save()

        n2 = Notification.objects.create(recipient=self.recipient_user, verb="Second notification.")
        n2.created_at = timezone.now() - timedelta(minutes=1)
        n2.save()

        n3 = Notification.objects.create(recipient=self.recipient_user, verb="Third (most recent) notification.")
        # n3.created_at will be timezone.now() by auto_now_add

        notifications = Notification.objects.filter(recipient=self.recipient_user)
        # Default ordering is '-created_at' as per model Meta
        self.assertEqual(list(notifications), [n3, n2, n1])
