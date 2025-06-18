from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from universities.models import University, Faculty, Course
from discussions.models import DiscussionThread, Post # Use direct import

User = get_user_model()

class DiscussionThreadModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="thread_starter", password="password123")
        cls.university = University.objects.create(name="Discussion Test University", city="DTU City")
        cls.faculty = Faculty.objects.create(university=cls.university, name="Discussion Test Faculty")
        cls.course = Course.objects.create(faculty=cls.faculty, code="DT101", title="Discussion Testing 101", year_offered=1)

    def test_create_discussion_thread(self):
        thread = DiscussionThread.objects.create(
            course=self.course,
            title="Test Thread Title",
            created_by=self.user1
        )
        self.assertEqual(thread.course, self.course)
        self.assertEqual(thread.title, "Test Thread Title")
        self.assertEqual(thread.created_by, self.user1)
        self.assertTrue(thread.is_active) # Default
        self.assertEqual(str(thread), f"Thread: Test Thread Title in {self.course.code}")

    def test_discussion_thread_get_absolute_url(self):
        thread = DiscussionThread.objects.create(
            course=self.course, title="URL Thread", created_by=self.user1
        )
        expected_url = f"/discussions/thread/{thread.pk}/"
        self.assertEqual(thread.get_absolute_url(), expected_url)


class PostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_thread_starter = User.objects.create_user(username="post_thread_starter", password="password")
        cls.user_post_author = User.objects.create_user(username="post_author", password="password")

        cls.university = University.objects.create(name="Post Test University", city="PTU City")
        cls.faculty = Faculty.objects.create(university=cls.university, name="Post Test Faculty")
        cls.course = Course.objects.create(faculty=cls.faculty, code="PT101", title="Post Testing 101", year_offered=1)

        cls.thread = DiscussionThread.objects.create(
            course=cls.course,
            title="Thread for Posts",
            created_by=cls.user_thread_starter
        )
        cls.another_thread = DiscussionThread.objects.create(
            course=cls.course,
            title="Another Thread",
            created_by=cls.user_thread_starter
        )


    def test_create_post(self):
        post = Post.objects.create(
            thread=self.thread,
            author=self.user_post_author,
            body="This is a test post body."
        )
        self.assertEqual(post.thread, self.thread)
        self.assertEqual(post.author, self.user_post_author)
        self.assertEqual(post.body, "This is a test post body.")
        self.assertIsNone(post.parent) # Top-level post
        self.assertTrue(post.is_active) # Default
        self.assertEqual(str(post), f"Post by {self.user_post_author.username} in {self.thread.title}")

    def test_post_nesting_validation_ok(self):
        parent_post = Post.objects.create(thread=self.thread, author=self.user_post_author, body="Parent post.")
        reply_post = Post(thread=self.thread, author=self.user_thread_starter, body="Reply post.", parent=parent_post)

        try:
            reply_post.full_clean() # Should not raise ValidationError
            reply_post.save()
        except ValidationError as e:
            self.fail(f"ValidationError raised unexpectedly: {e}")

        self.assertEqual(reply_post.parent, parent_post)
        self.assertEqual(parent_post.replies.count(), 1)

    def test_post_nesting_validation_too_deep(self):
        parent_post = Post.objects.create(thread=self.thread, author=self.user_post_author, body="Parent post.")
        reply_to_parent = Post.objects.create(thread=self.thread, author=self.user_thread_starter, body="First reply.", parent=parent_post)

        reply_to_reply = Post(thread=self.thread, author=self.user_post_author, body="Reply to a reply.", parent=reply_to_parent)

        with self.assertRaisesMessage(ValidationError, "Replies cannot be nested more than one level deep."):
            reply_to_reply.full_clean()

    def test_post_parent_different_thread_validation(self):
        parent_post_in_another_thread = Post.objects.create(thread=self.another_thread, author=self.user_post_author, body="Parent in wrong thread.")

        reply_post = Post(thread=self.thread, author=self.user_thread_starter, body="Reply post.", parent=parent_post_in_another_thread)

        with self.assertRaisesMessage(ValidationError, "The parent post must belong to the same discussion thread."):
            reply_post.full_clean()

    def test_post_get_absolute_url(self):
        post = Post.objects.create(
            thread=self.thread, author=self.user_post_author, body="URL Test Post"
        )
        expected_url = f"/discussions/thread/{self.thread.pk}/#post-{post.pk}"
        self.assertEqual(post.get_absolute_url(), expected_url)
