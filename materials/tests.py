from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile # For dummy file
from taggit.models import Tag

from universities.models import University, Faculty, Course
from materials.models import Material, MaterialTypeChoices # Changed to absolute import

User = get_user_model()

class MaterialModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="uploader", password="password123")
        cls.university = University.objects.create(name="Material Test University", city="MTU City")
        cls.faculty = Faculty.objects.create(university=cls.university, name="Material Test Faculty")
        cls.course = Course.objects.create(faculty=cls.faculty, code="MT101", title="Material Testing 101", year_offered=1)

    def test_create_material(self):
        # Create a dummy file for the FileField
        dummy_file = SimpleUploadedFile("test_material.txt", b"Some file content.", content_type="text/plain")

        material = Material.objects.create(
            course=self.course,
            uploaded_by=self.user,
            title="Test Material Title",
            file=dummy_file,
            material_type=MaterialTypeChoices.NOTES,
            description="A test material description."
        )
        self.assertEqual(material.course, self.course)
        self.assertEqual(material.uploaded_by, self.user)
        self.assertEqual(material.title, "Test Material Title")
        self.assertTrue(material.file.name.startswith('materials/'))  # Check general path structure
        # Check if the original filename is part of the stored filename's basename
        import os
        file_basename = os.path.basename(material.file.name)
        self.assertTrue(file_basename.startswith('test_material'))
        self.assertTrue(file_basename.endswith('.txt'))
        self.assertEqual(material.material_type, MaterialTypeChoices.NOTES)
        self.assertEqual(material.description, "A test material description.")
        self.assertEqual(material.download_count, 0) # Default
        self.assertTrue(material.is_active) # Default
        self.assertEqual(str(material), f"Test Material Title for {self.course.code}")

    def test_material_file_upload_path_generation(self):
        # Test the dynamic path generation (e.g., 'materials/%Y/%m/%d/')
        from django.utils import timezone
        now = timezone.now()
        expected_path_segment = now.strftime('materials/%Y/%m/%d/')

        dummy_file = SimpleUploadedFile("path_test.pdf", b"PDF content", content_type="application/pdf")
        material = Material.objects.create(
            course=self.course,
            uploaded_by=self.user,
            title="Path Test Material",
            file=dummy_file,
            material_type=MaterialTypeChoices.PAST_PAPER
        )
        self.assertTrue(material.file.name.startswith(expected_path_segment))

    def test_material_tags(self):
        dummy_file = SimpleUploadedFile("tagged_material.docx", b"Word content", content_type="application/msword")
        material = Material.objects.create(
            course=self.course,
            uploaded_by=self.user,
            title="Tagged Material",
            file=dummy_file
        )
        material.tags.add("test_tag1", "test_tag2")
        material.save()

        retrieved_material = Material.objects.get(pk=material.pk)
        self.assertEqual(retrieved_material.tags.count(), 2)
        tag_names = [tag.name for tag in retrieved_material.tags.all()]
        self.assertIn("test_tag1", tag_names)
        self.assertIn("test_tag2", tag_names)

    def test_material_type_choices_and_default(self):
        dummy_file = SimpleUploadedFile("default_type.zip", b"Zip archive", content_type="application/zip")
        material = Material.objects.create(
            course=self.course,
            uploaded_by=self.user,
            title="Default Type Material",
            file=dummy_file
            # material_type is not specified, should use default
        )
        self.assertEqual(material.material_type, MaterialTypeChoices.OTHER) # Check default

        material.material_type = MaterialTypeChoices.ASSIGNMENT
        material.save()
        retrieved_material = Material.objects.get(pk=material.pk)
        self.assertEqual(retrieved_material.material_type, MaterialTypeChoices.ASSIGNMENT)

    def test_material_get_absolute_url(self):
        dummy_file = SimpleUploadedFile("url_material.txt", b"content", content_type="text/plain")
        material = Material.objects.create(
            course=self.course,
            uploaded_by=self.user,
            title="URL Material",
            file=dummy_file,
        )
        expected_url = f"/materials/course/{self.course.pk}/#material-{material.pk}"
        self.assertEqual(material.get_absolute_url(), expected_url)


from django.test import Client # For integration tests
from django.urls import reverse
import os # For os.path.basename

class MaterialFlowIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser_integration',
            email='test_integration@example.com',
            password='password'
        )
        cls.uni = University.objects.create(name='Integration Test University', city='Integration City')
        cls.faculty = Faculty.objects.create(university=cls.uni, name='Integration Test Faculty')
        cls.course = Course.objects.create(
            faculty=cls.faculty,
            code='INT101',
            title='Integration Testing',
            year_offered=1
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser_integration', password='password')

    def test_material_upload_list_download_flow(self):
        # 1. Upload
        upload_url = reverse('materials:material_upload')
        file_content = b'This is a test PDF content for integration test.'
        dummy_file = SimpleUploadedFile(
            'integration_test_doc.pdf',
            file_content,
            content_type='application/pdf'
        )
        form_data = {
            'title': 'Integration Test Material',
            'course': self.course.pk,
            'material_type': MaterialTypeChoices.NOTES,
            'description': 'An integration test material description.',
            'file': dummy_file,
            # 'tags': 'integration, test' # Optional
        }

        response = self.client.post(upload_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200) # Should land on course detail page
        self.assertTemplateUsed(response, 'materials/course_detail.html')

        # Verify material creation
        self.assertTrue(
            Material.objects.filter(title='Integration Test Material', course=self.course).exists()
        )
        material = Material.objects.get(title='Integration Test Material', course=self.course)

        # 2. List (on Course Detail Page)
        # The previous response is already for the course detail page due to follow=True
        self.assertContains(response, material.title)
        self.assertContains(response, material.description)
        self.assertContains(response, reverse('materials:material_download', kwargs={'pk': material.pk}))

        # 3. Download
        download_url = reverse('materials:material_download', kwargs={'pk': material.pk})
        initial_download_count = material.download_count

        download_response = self.client.get(download_url)
        self.assertEqual(download_response.status_code, 200)
        self.assertTrue(download_response.has_header('Content-Disposition'))
        # Use os.path.basename for robust filename checking in Content-Disposition
        expected_filename = os.path.basename(material.file.name)
        self.assertIn(f'attachment; filename="{expected_filename}"', download_response['Content-Disposition'])
        self.assertEqual(download_response.get('content-type'), 'application/pdf') # Check content type

        # Check streaming content (optional, but good for verification)
        # Convert streaming content to bytes and compare
        streamed_content = b"".join(download_response.streaming_content)
        self.assertEqual(streamed_content, file_content)

        # Verify download count incremented
        material.refresh_from_db()
        self.assertEqual(material.download_count, initial_download_count + 1)
