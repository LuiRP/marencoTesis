from django.urls import path, include
from .views import (
    index,
    tutorships,
    tutorship_create,
    tutorship_update,
    tutorship_delete,
)

urlpatterns = [
    path("", index, name="index"),
    path("tutorships/", tutorships, name="tutorships"),
    path("tutorships/create", tutorship_create, name="tutorship_create"),
    path(
        "tutorships/edit/<int:tutorship_id>", tutorship_update, name="tutorship_update"
    ),
    path(
        "tutorships/delete/<int:tutorship_id>",
        tutorship_delete,
        name="tutorship_delete",
    ),
]
