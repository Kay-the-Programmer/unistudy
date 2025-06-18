from django.contrib import admin
from .models import DiscussionThread, Post
from django.utils.html import format_html
from django.urls import reverse

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'created_by_username', 'created_at', 'is_active')
    search_fields = ('title', 'course__code', 'course__title', 'created_by__username')
    list_filter = ('course__faculty__university', 'course__faculty', 'is_active', 'created_at')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ['course', 'created_by']

    def course_code(self, obj):
        return obj.course.code
    course_code.short_description = 'Course Code'
    course_code.admin_order_field = 'course__code'

    def created_by_username(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return None
    created_by_username.short_description = 'Created By'
    created_by_username.admin_order_field = 'created_by__username'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author_username', 'thread_link', 'created_at', 'parent_summary_link', 'is_active', 'short_body')
    search_fields = ('author__username', 'thread__title', 'body')
    list_filter = ('thread__course__faculty__university', 'is_active', 'created_at', 'thread__course__faculty')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ['thread', 'author', 'parent']
    readonly_fields = ('parent_summary_link_readonly', 'thread_link_readonly')


    def author_username(self, obj):
        if obj.author:
            return obj.author.username
        return 'Anonymous'
    author_username.short_description = 'Author'
    author_username.admin_order_field = 'author__username'

    def thread_link(self, obj):
        link = reverse("admin:discussions_discussionthread_change", args=[obj.thread.id])
        return format_html('<a href="{}">{}</a>', link, obj.thread.title)
    thread_link.short_description = 'Thread Title'
    thread_link.admin_order_field = 'thread__title'

    def thread_link_readonly(self, obj): # For readonly_fields
        return self.thread_link(obj)
    thread_link_readonly.short_description = 'Thread Title'


    def parent_summary_link(self, obj):
        if obj.parent:
            link = reverse("admin:discussions_post_change", args=[obj.parent.id])
            return format_html('<a href="{}">Post #{} by {}</a>', link, obj.parent.id, obj.parent.author.username if obj.parent.author else "Anonymous")
        return "-"
    parent_summary_link.short_description = 'Parent Post'

    def parent_summary_link_readonly(self, obj): # For readonly_fields
        return self.parent_summary_link(obj)
    parent_summary_link_readonly.short_description = 'Parent Post'

    def short_body(self, obj):
        from django.utils.text import Truncator
        return Truncator(obj.body).words(10, truncate=' ...')
    short_body.short_description = 'Body (excerpt)'
