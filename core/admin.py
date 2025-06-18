from django.contrib import admin
from .models import Notification
from django.utils.html import format_html, escape
from django.urls import reverse, NoReverseMatch


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient_username",
        "verb",
        "target_summary_link",
        "action_object_summary_link",
        "is_read",
        "created_at",
    )  # noqa: E501
    search_fields = ("recipient__username", "verb")
    list_filter = (
        "is_read",
        "created_at",
        "recipient__username",
    )  # Changed recipient to recipient__username for filtering
    list_editable = ("is_read",)
    date_hierarchy = "created_at"
    autocomplete_fields = ["recipient"]  # For recipient ForeignKey
    readonly_fields = ("target_summary_link_readonly", "action_object_summary_link_readonly")

    def recipient_username(self, obj):
        return obj.recipient.username

    recipient_username.short_description = "Recipient"
    recipient_username.admin_order_field = "recipient__username"

    def _get_obj_summary_link(self, obj, field_name_prefix):
        content_type = getattr(obj, f"{field_name_prefix}_content_type")
        object_id = getattr(obj, f"{field_name_prefix}_object_id")
        gfk_obj = getattr(obj, field_name_prefix)

        if not content_type or not object_id or not gfk_obj:
            return "-"

        obj_str = escape(str(gfk_obj))

        # Try to create a link to the admin change page for the object
        try:
            admin_url = reverse(
                f"admin:{content_type.app_label}_{content_type.model}_change", args=(object_id,)
            )
            return format_html('<a href="{}">{}</a>', admin_url, obj_str)
        except NoReverseMatch:
            # If no admin page is registered or URL is not found, just return the string representation
            return obj_str

    def target_summary_link(self, obj):
        return self._get_obj_summary_link(obj, "target")

    target_summary_link.short_description = "Target Object"

    def target_summary_link_readonly(self, obj):  # For readonly_fields
        return self.target_summary_link(obj)

    target_summary_link_readonly.short_description = "Target Object"

    def action_object_summary_link(self, obj):
        return self._get_obj_summary_link(obj, "action_object")

    action_object_summary_link.short_description = "Action Object"

    def action_object_summary_link_readonly(self, obj):  # For readonly_fields
        return self.action_object_summary_link(obj)

    action_object_summary_link_readonly.short_description = "Action Object"
