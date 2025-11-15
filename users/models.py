from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


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
