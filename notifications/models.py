from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# Create your models here.
class Notification(models.Model):
    NOTIFICATION_TYPE = [
        ("reseña", "Reseña"),
        ("reserva", "Reserva"),
        ("mensaje", "Mensaje"),
    ]
    type = models.CharField("Tipo de Notificación", choices=NOTIFICATION_TYPE)
    body = models.TextField("Cuerpo de la notificación")
    action_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_who_did_action"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_who_receives"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
