from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# Create your models here.
class ChatThread(models.Model):
    user1 = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="chat_threads_as_user1"
    )
    user2 = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="chat_threads_as_user2"
    )

    class Meta:
        unique_together = ("user1", "user2")

    def get_ordered_users(self):
        return sorted([self.user1, self.user2], key=lambda u: u.id)

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"


class Message(models.Model):
    thread = models.ForeignKey(
        ChatThread, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("timestamp",)

    def __str__(self):
        return (
            f"Message by {self.sender.username} at {self.timestamp.strftime('%H:%M')}"
        )
