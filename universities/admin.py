from django.contrib import admin
from .models import University, Faculty, Course

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'slug')
    search_fields = ('name', 'city')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'slug')
    search_fields = ('name', 'university__name')
    list_filter = ('university',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'faculty', 'year_offered')
    search_fields = ('code', 'title', 'faculty__name', 'faculty__university__name')
    list_filter = ('faculty__university', 'faculty', 'year_offered')
