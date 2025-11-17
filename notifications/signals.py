# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        user_notifications = cache.get(f"user_{instance.receiver.id}_notifications", [])

        notification_data = {
            "id": instance.id,
            "type": instance.type,
            "body": instance.body,
            "action_user": instance.action_user.id,
            "receiver": instance.receiver.id,
            "created_at": instance.created_at.isoformat(),
        }

        user_notifications.append(notification_data)
        cache.set(
            f"user_{instance.receiver.id}_notifications",
            user_notifications,
            timeout=300,
        )
