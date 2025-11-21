from django.urls import path, include
from .views import (
    index,
    tutorships,
    tutorship_create,
    tutorship_update,
    tutorship_delete,
    timetable,
    create_timetable,
    save_time_range,
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
    path("timetable/", timetable, name="timetable"),
    path("timetable/create", create_timetable, name="create_timetable"),
]
