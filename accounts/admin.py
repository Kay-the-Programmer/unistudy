from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "university", "programme", "year_of_study", "avatar_thumbnail")
    search_fields = ("user__username", "user__email", "university__name", "programme")
    list_filter = ("university", "year_of_study")
    readonly_fields = ("avatar_thumbnail",)  # To display the image

    def avatar_thumbnail(self, obj):
        from django.utils.html import format_html

        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "-"

    avatar_thumbnail.short_description = "Avatar"
