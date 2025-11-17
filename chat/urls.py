from django.urls import path, include
from .views import inbox, get_or_create_chat_thread

urlpatterns = [
    path("inbox/", inbox, name="inbox"),
    path(
        "get_chat/<int:other_user_id>",
        get_or_create_chat_thread,
        name="get_or_create_chat_thread",
    ),
]
