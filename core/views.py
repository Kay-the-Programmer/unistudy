from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required # Corrected import
from django.views.generic import TemplateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

# from django.contrib.contenttypes.models import ContentType # No longer directly used
from django.contrib import messages
from django.urls import reverse_lazy, reverse  # Added reverse
from django import forms  # Added forms
from django.http import Http404  # Already imported

from .models import Notification
from materials.models import Material
from discussions.models import Post
from .notifications import create_bulk_notifications  # Import notification helper
from django.contrib.auth import get_user_model

User = get_user_model()


# Staff check function (already present)
def is_staff_user(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user)  # Or @staff_member_required
def moderation_dashboard(request):
    # Fetch reported items (Notifications to staff about reports)
    # Assuming the verb for reports is like "User X reported Y"
    # and the target of the notification is the reported content (Material or Post)
    reported_notifications = Notification.objects.filter(
        recipient__is_staff=True, verb__icontains="reported"  # Or a specific staff group
    ).order_by("-created_at")[
        :20
    ]  # Get recent 20 reports

    # Fetch some inactive content for quick review
    inactive_materials = Material.objects.filter(is_active=False).order_by("-created_at")[:5]
    inactive_posts = Post.objects.filter(is_active=False).order_by("-created_at")[:5]

    context = {
        "reported_notifications": reported_notifications,
        "inactive_materials": inactive_materials,
        "inactive_posts": inactive_posts,
    }
    return render(request, "core/moderation_dashboard.html", context)


class LandingPageView(TemplateView):
    template_name = "core/landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["welcome_message"] = "Welcome to ZStudy - Your Academic Hub!"
        # Later, this could fetch recent materials, discussions, etc.
        # For example:
        # context['recent_materials'] = Material.objects.filter(is_active=True).order_by('-created_at')[:5]  # noqa: E501
        # context['recent_threads'] = DiscussionThread.objects.filter(is_active=True).order_by('-created_at')[:5]  # noqa: E501
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "core/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 15  # Optional: if you expect many notifications

    def get_queryset(self):
        # Get notifications for the current user
        queryset = super().get_queryset().filter(recipient=self.request.user)

        # Mark unread notifications as read upon fetching them. This is a common pattern.
        # unread_notifications = queryset.filter(is_read=False) # F841: local var assigned but not used
        # for notification in unread_notifications: notification.is_read = True; # noqa: E501, E701
        # Notification.objects.bulk_update(unread_notifications, ['is_read']) # Better, but complex. # noqa: E501
        # Simplest: update then fetch again or rely on template. # noqa: E501
        # Robust: AJAX call to mark as read. # noqa: E501

        # For simplicity, we'll just fetch them. Marking as read can be a separate explicit action.
        # Or, assume viewing the list marks them as "seen" conceptually.
        # For actual marking as read:
        # ids_to_update = list(unread_notifications.values_list('id', flat=True))
        # Notification.objects.filter(id__in=ids_to_update).update(is_read=True)
        # queryset = super().get_queryset().filter(recipient=self.request.user) # Re-fetch after update

        # The prompt states "mark as read on access".
        # Be careful with bulk updates and signals if any exist on Notification model.
        # For now, let's do a simple update.
        Notification.objects.filter(recipient=self.request.user, is_read=False).update(
            is_read=True
        )
        return queryset.order_by("-created_at")  # Show newest first


class GlobalSearchView(ListView):
    model = Material  # Base model for searching
    template_name = "core/search_results.html"
    context_object_name = "results"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if query:
            # Search in title and tags (case-insensitive)
            # Using distinct() to avoid duplicates if a material matches both title and tag
            return Material.objects.filter(
                (Q(title__icontains=query) | Q(tags__name__icontains=query))
                & Q(is_active=True)
            ).distinct().select_related("course", "uploaded_by").prefetch_related("tags")  # noqa: E501
        return Material.objects.none()  # Return no results if query is empty

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


@staff_member_required
def toggle_active_status(request, model_name, object_id):
    try:
        allowed_models_map = {
            "material": Material,
            "post": Post,
        }
        if model_name not in allowed_models_map:
            raise Http404("Invalid model type specified.")

        model_class = allowed_models_map[model_name]
        obj = get_object_or_404(model_class, pk=object_id)

        obj.is_active = not obj.is_active
        obj.save()
        status_msg = (
            f"{model_name.capitalize()} '{str(obj)[:50]}' status changed to "
            f"{'Active' if obj.is_active else 'Inactive'}."
        )  # noqa: E501
        messages.success(request, status_msg)
    except Http404:
        messages.error(request, "Item not found.")
    except Exception as e:
        messages.error(request, f"Error changing status: {e}")

    return redirect(request.META.get("HTTP_REFERER", "core:moderation_dashboard"))


# Simple form for confirmation
class ReportConfirmationForm(forms.Form):
    # No fields needed, just a CSRF token and a submit button
    pass


class ReportContentView(LoginRequiredMixin, FormView):
    form_class = ReportConfirmationForm
    template_name = "core/report_confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        self.model_name = kwargs.get("model_name")
        self.object_id = kwargs.get("object_id")

        allowed_models_map = {"material": Material, "post": Post}
        if self.model_name not in allowed_models_map:
            raise Http404("Invalid content type for reporting.")

        self.model_class = allowed_models_map[self.model_name]
        self.content_object = get_object_or_404(self.model_class, pk=self.object_id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_object"] = self.content_object
        context["model_name"] = self.model_name
        return context

    def form_valid(self, form):
        reporter = self.request.user
        staff_users = User.objects.filter(is_staff=True)

        verb = (
            f"Content reported by {reporter.username}: A {self.model_name} "
            f"titled '{str(self.content_object)[:50]}'."
        )  # noqa: E501

        # Use reporter's profile as action_object if it exists, otherwise the reporter user object
        action_object_for_notification = getattr(reporter, "profile", reporter)

        create_bulk_notifications(
            recipient_qs=staff_users,
            verb=verb,
            action_object=action_object_for_notification,  # The user profile/user reporting
            target=self.content_object,  # The content being reported
            actor=reporter,  # The user who performed the report action
        )

        messages.success(self.request, "Thank you for your report. Staff have been notified.")

        # Try to redirect to the object's absolute URL if it exists, otherwise to a generic page
        if hasattr(self.content_object, "get_absolute_url"):
            return redirect(self.content_object.get_absolute_url())
        return redirect(reverse("core:landing_page"))  # Fallback redirect

    def get_success_url(self):
        # This is called by FormView if form_valid doesn't return an HttpResponse.
        # We are returning redirect in form_valid, so this might not be strictly necessary
        # unless form_valid calls super().form_valid() which then calls this.
        if hasattr(self.content_object, "get_absolute_url"):
            return self.content_object.get_absolute_url()
        return reverse_lazy("core:landing_page")
