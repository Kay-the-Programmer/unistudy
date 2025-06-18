from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from decimal import Decimal # If you have DecimalFields

from universities.models import University, Faculty, Course
from accounts.models import UserProfile # Assuming signals create UserProfile
# Import other models as needed: Material, DiscussionThread, Post, Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Loads sample data into the database for development and testing.'

    def _get_or_create_user(self, username, password, email, is_staff=False, is_superuser=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': is_staff, 'is_superuser': is_superuser}
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User "{username}" created.'))
        else:
            # Ensure password is set if user already exists but might not have one (e.g. from prior manual creation)
            if not user.has_usable_password():
                user.set_password(password)
                user.save()
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists.'))
        return user

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load sample data...'))

        # Create Users
        admin_user = self._get_or_create_user('admin', 'adminpass', 'admin@zstudy.com', is_staff=True, is_superuser=True)
        user1 = self._get_or_create_user('user1', 'user1pass', 'user1@zstudy.com')
        user2 = self._get_or_create_user('user2', 'user2pass', 'user2@zstudy.com')

        # Create Universities
        unza, _ = University.objects.get_or_create(name='University of Zambia', defaults={'city': 'Lusaka', 'slug': slugify('University of Zambia')})
        cbu, _ = University.objects.get_or_create(name='Copperbelt University', defaults={'city': 'Kitwe', 'slug': slugify('Copperbelt University')})
        mulungushi, _ = University.objects.get_or_create(name='Mulungushi University', defaults={'city': 'Kabwe', 'slug': slugify('Mulungushi University')})

        # Create Faculties
        unza_eng, _ = Faculty.objects.get_or_create(university=unza, name='School of Engineering', defaults={'slug': slugify('School of Engineering')})
        unza_nas, _ = Faculty.objects.get_or_create(university=unza, name='School of Natural Sciences', defaults={'slug': slugify('School of Natural Sciences')})
        cbu_sbt, _ = Faculty.objects.get_or_create(university=cbu, name='School of Business', defaults={'slug': slugify('School of Business')})
        cbu_ict, _ = Faculty.objects.get_or_create(university=cbu, name='School of ICT', defaults={'slug': slugify('School of ICT')})

        # Create Courses
        Course.objects.get_or_create(faculty=unza_eng, code='CEE2210', title='Civil Engineering Materials', defaults={'year_offered': 2})
        Course.objects.get_or_create(faculty=unza_eng, code='CSE3100', title='Operating Systems', defaults={'year_offered': 3})
        Course.objects.get_or_create(faculty=unza_nas, code='CSC1100', title='Introduction to Computer Science', defaults={'year_offered': 1})
        Course.objects.get_or_create(faculty=cbu_sbt, code='BS110', title='Introduction to Business Management', defaults={'year_offered': 1})
        Course.objects.get_or_create(faculty=cbu_ict, code='ICT1110', title='Introduction to Programming', defaults={'year_offered': 1})

        # Link UserProfiles to Universities & add details
        try:
            if hasattr(user1, 'profile'):
                user1.profile.university = unza
                user1.profile.programme = "BEng Civil Engineering"
                user1.profile.year_of_study = 2
                user1.profile.save()
                self.stdout.write(f'Updated profile for {user1.username}.')

            if hasattr(user2, 'profile'):
                user2.profile.university = cbu
                user2.profile.programme = "BSc Computer Science"
                user2.profile.year_of_study = 1
                user2.profile.save()
                self.stdout.write(f'Updated profile for {user2.username}.')

            if hasattr(admin_user, 'profile'): # Admin might not have a typical student profile
                admin_user.profile.university = unza # Or leave None
                admin_user.profile.save()
                self.stdout.write(f'Updated profile for {admin_user.username}.')

        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.WARNING('UserProfile not found for a user, possibly due to signal timing or issue.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating user profiles: {e}'))


        # TODO: Add sample materials, discussions, posts, notifications as needed.
        # Example Material:
        # from django.core.files.uploadedfile import SimpleUploadedFile
        # from materials.models import Material, MaterialTypeChoices
        # csc1100 = Course.objects.get(code='CSC1100', faculty=unza_nas)
        # dummy_file = SimpleUploadedFile("intro_notes.pdf", b"Introduction to CS lecture notes.", content_type="application/pdf")
        # Material.objects.get_or_create(
        #     course=csc1100,
        #     uploaded_by=user1, # Or admin_user
        #     title="Intro to CS Lecture Notes Week 1",
        #     material_type=MaterialTypeChoices.NOTES,
        #     defaults={'file': dummy_file, 'description': "Sample lecture notes for CSC1100."}
        # )

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data.'))
