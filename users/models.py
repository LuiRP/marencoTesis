from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(
        _("email addres"),
        unique=True,
    )

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        null=True,
        blank=True,
        default="profile_pics/default.jpg",
    )

    is_tutor = models.BooleanField(default=False)
    description = models.TextField("description", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Review(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="authored_reviews"
    )
    reviewed = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_reviews"
    )
    body = models.TextField("Cuerpo de la reseña")
    rating = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
