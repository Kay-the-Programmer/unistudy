from django.contrib import admin
from .models import Material

@admin.action(description='Mark selected materials as active')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description='Mark selected materials as inactive')
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'material_type', 'uploaded_by_username', 'created_at', 'download_count', 'is_active')
    search_fields = ('title', 'course__code', 'course__title', 'uploaded_by__username', 'tags__name')
    list_filter = ('material_type', 'course__faculty__university', 'course__faculty', 'is_active', 'created_at')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    actions = [make_active, make_inactive]
    autocomplete_fields = ['course', 'uploaded_by', 'tags'] # For better UX with ForeignKey and M2M

    def course_code(self, obj):
        return obj.course.code
    course_code.short_description = 'Course Code'
    course_code.admin_order_field = 'course__code'

    def uploaded_by_username(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None
    uploaded_by_username.short_description = 'Uploaded By'
    uploaded_by_username.admin_order_field = 'uploaded_by__username'
