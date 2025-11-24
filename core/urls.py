from django.urls import path, include
from .views import (
    index,
    tutorships,
    tutorship_create,
    tutorship_update,
    tutorship_delete,
    timetable,
    create_timetable,
    edit_timetable,
    delete_timetable,
    add_student,
    remove_student,
    get_unread_count,
    get_unread_count_notifications,
)

urlpatterns = [
    path("", index, name="index"),
    path("tutorships/", tutorships, name="tutorships"),
    path("unread-count/", get_unread_count, name="unread_count"),
    path(
        "unread-count-notifications/",
        get_unread_count_notifications,
        name="unread_count_notifications",
    ),
    path("tutorships/create", tutorship_create, name="tutorship_create"),
    path(
        "tutorships/edit/<int:tutorship_id>", tutorship_update, name="tutorship_update"
    ),
    path(
        "tutorships/delete/<int:tutorship_id>",
        tutorship_delete,
        name="tutorship_delete",
    ),
    path("timetable/<int:user_id>", timetable, name="timetable"),
    path("timetable/create/<str:week_day>", create_timetable, name="create_timetable"),
    path("timetable/edit/<int:period_id>/", edit_timetable, name="edit_timetable"),
    path(
        "timetable/delete/<int:period_id>/", delete_timetable, name="delete_timetable"
    ),
    path("timetable/add_student/<int:period_id>/", add_student, name="add_student"),
    path(
        "timetable/remove_student/<int:period_id>/",
        remove_student,
        name="remove_student",
    ),
]
