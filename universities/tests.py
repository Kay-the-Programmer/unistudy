from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils.text import slugify

from .models import University, Faculty, Course

class UniversityModelTests(TestCase):
    def test_create_university(self):
        uni = University.objects.create(name="Test University One", city="Testville")
        self.assertEqual(uni.name, "Test University One")
        self.assertEqual(uni.city, "Testville")
        self.assertEqual(uni.slug, slugify("Test University One")) # Slug auto-generated
        self.assertEqual(str(uni), "Test University One")

    def test_university_slug_auto_generation(self):
        uni = University.objects.create(name="Another Test Uni", city="Cityville")
        self.assertIsNotNone(uni.slug)
        self.assertEqual(uni.slug, slugify("Another Test Uni"))

    def test_university_name_unique(self):
        University.objects.create(name="Unique Name Uni", city="AnyCity")
        with self.assertRaises(IntegrityError):
            University.objects.create(name="Unique Name Uni", city="OtherCity")

    def test_university_slug_unique(self):
        University.objects.create(name="Uni With Slug", city="AnyCity", slug="unique-slug-1")
        with self.assertRaises(IntegrityError):
            University.objects.create(name="Other Uni With Slug", city="OtherCity", slug="unique-slug-1")


class FacultyModelTests(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Test University for Faculty", city="Unicity")

    def test_create_faculty(self):
        faculty = Faculty.objects.create(university=self.university, name="Faculty of Science")
        self.assertEqual(faculty.name, "Faculty of Science")
        self.assertEqual(faculty.university, self.university)
        self.assertEqual(faculty.slug, slugify("Faculty of Science")) # Slug auto-generated
        self.assertEqual(str(faculty), f"Faculty of Science, {self.university.name}")

    def test_faculty_slug_auto_generation(self):
        faculty = Faculty.objects.create(university=self.university, name="Faculty of Arts")
        self.assertIsNotNone(faculty.slug)
        self.assertEqual(faculty.slug, slugify("Faculty of Arts"))

    def test_faculty_unique_constraint_university_name(self):
        Faculty.objects.create(university=self.university, name="Unique Faculty Name")
        with self.assertRaises(IntegrityError):
            Faculty.objects.create(university=self.university, name="Unique Faculty Name")

    def test_faculty_slug_unique_within_university(self):
        # Note: Slug must be unique *per university*.
        Faculty.objects.create(university=self.university, name="Faculty A", slug="faculty-slug-a")
        with self.assertRaises(IntegrityError):
            Faculty.objects.create(university=self.university, name="Faculty B", slug="faculty-slug-a")

    def test_faculty_slug_can_be_reused_across_universities(self):
        # Ensure slug can be reused with different uni
        Faculty.objects.create(university=self.university, name="Faculty X", slug="reusable-slug")
        other_uni = University.objects.create(name="Other University", city="Otherville")
        Faculty.objects.create(university=other_uni, name="Faculty Y", slug="reusable-slug")
        self.assertTrue(Faculty.objects.filter(university=other_uni, slug="reusable-slug").exists())


class CourseModelTests(TestCase):
    def setUp(self):
        self.university = University.objects.create(name="Test University for Course", city="Courseville")
        self.faculty = Faculty.objects.create(university=self.university, name="Engineering Faculty")

    def test_create_course(self):
        course = Course.objects.create(
            faculty=self.faculty,
            code="CS101",
            title="Intro to CS",
            year_offered=1
        )
        self.assertEqual(course.code, "CS101")
        self.assertEqual(course.title, "Intro to CS")
        self.assertEqual(course.year_offered, 1)
        self.assertEqual(course.faculty, self.faculty)
        self.assertEqual(str(course), f"CS101 - Intro to CS ({self.faculty.name})")

    def test_course_unique_constraint_faculty_code(self):
        Course.objects.create(faculty=self.faculty, code="EE202", title="Digital Circuits", year_offered=2)
        with self.assertRaises(IntegrityError):
            Course.objects.create(faculty=self.faculty, code="EE202", title="Advanced Circuits", year_offered=2)

    def test_course_unique_constraint_faculty_title(self):
        Course.objects.create(faculty=self.faculty, code="ME303", title="Thermodynamics", year_offered=3)
        with self.assertRaises(IntegrityError):
            Course.objects.create(faculty=self.faculty, code="ME304", title="Thermodynamics", year_offered=3)
