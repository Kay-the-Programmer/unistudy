from .models import Notification  # Assuming Notification model is in core.models


def unread_notifications_count_processor(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {"unread_notifications_count": count}
    return {"unread_notifications_count": 0}
