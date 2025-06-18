from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Notification # Assuming Notification model is in core.models
from materials.models import Material # Import Material model

# Staff check function (already present)
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_staff_user)
def moderation_dashboard(request):
    # This is a placeholder. In a real scenario, you might fetch data for moderation here.
    return render(request, 'core/moderation_dashboard.html')

class LandingPageView(TemplateView):
    template_name = 'core/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['welcome_message'] = "Welcome to ZStudy - Your Academic Hub!"
        # Later, this could fetch recent materials, discussions, etc.
        # For example:
        # context['recent_materials'] = Material.objects.filter(is_active=True).order_by('-created_at')[:5]
        # context['recent_threads'] = DiscussionThread.objects.filter(is_active=True).order_by('-created_at')[:5]
        return context

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'core/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 15 # Optional: if you expect many notifications

    def get_queryset(self):
        # Get notifications for the current user
        queryset = super().get_queryset().filter(recipient=self.request.user)

        # Mark unread notifications as read upon fetching them
        # This is a common pattern. Alternatively, use a separate "mark as read" view/action.
        unread_notifications = queryset.filter(is_read=False)
        # for notification in unread_notifications: # This would be N queries
        #     notification.is_read = True
        # Notification.objects.bulk_update(unread_notifications, ['is_read']) # This is better but might not work with all backends for GFKs effectively if signals are involved.
        # Simplest for now, let's update and then fetch again or rely on template to show difference.
        # A more robust way would be an AJAX call to mark as read when notification is clicked/viewed.

        # For simplicity, we'll just fetch them. Marking as read can be a separate explicit action.
        # Or, more simply for now, let's assume viewing the list marks them as "seen" conceptually.
        # For actual marking as read:
        # ids_to_update = list(unread_notifications.values_list('id', flat=True))
        # Notification.objects.filter(id__in=ids_to_update).update(is_read=True)
        # queryset = super().get_queryset().filter(recipient=self.request.user) # Re-fetch after update

        # The prompt states "mark as read on access".
        # Be careful with bulk updates and signals if any exist on Notification model.
        # For now, let's do a simple update.
        Notification.objects.filter(recipient=self.request.user, is_read=False).update(is_read=True)
        return queryset.order_by('-created_at') # Show newest first

class GlobalSearchView(ListView):
    model = Material # Base model for searching
    template_name = 'core/search_results.html'
    context_object_name = 'results'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if query:
            # Search in title and tags (case-insensitive)
            # Using distinct() to avoid duplicates if a material matches both title and tag
            return Material.objects.filter(
                (Q(title__icontains=query) | Q(tags__name__icontains=query)) & Q(is_active=True)
            ).distinct().select_related('course', 'uploaded_by').prefetch_related('tags')
        return Material.objects.none() # Return no results if query is empty

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context
