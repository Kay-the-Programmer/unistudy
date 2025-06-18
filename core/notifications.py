from django.contrib.contenttypes.models import ContentType
from .models import Notification  # Assuming Notification model is in core.models
from django.contrib.auth import get_user_model

User = get_user_model()


def create_bulk_notifications(recipient_qs, verb, action_object=None, target=None, actor=None):
    """
    Creates notifications in bulk for a queryset of recipients.
    - recipient_qs: QuerySet of User objects.
    - verb: String describing the action.
    # - action_object: Object performing action or related to it (e.g. User, Material).
    - target: The object the action was performed on (e.g., Course, DiscussionThread).
    - actor: The User who performed the action (to avoid self-notification).
    """
    notifications_to_create = []

    action_object_content_type = None
    action_object_object_id = None
    if action_object:
        action_object_content_type = ContentType.objects.get_for_model(action_object)
        action_object_object_id = action_object.pk

    target_content_type = None
    target_object_id = None
    if target:
        target_content_type = ContentType.objects.get_for_model(target)
        target_object_id = target.pk

    for recipient in recipient_qs:
        if actor and recipient.pk == actor.pk:  # Avoid self-notification
            continue

        notifications_to_create.append(
            Notification(
                recipient=recipient,
                verb=verb,
                action_object_content_type=action_object_content_type,
                action_object_object_id=action_object_object_id,
                target_content_type=target_content_type,
                target_object_id=target_object_id,
            )
        )

    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        return len(notifications_to_create)
    return 0
