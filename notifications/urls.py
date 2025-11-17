from django.urls import path, include
from .views import notifications, sse_stream_notification

urlpatterns = [
    path("notifications/", notifications, name="notifications"),
    path(
        "stream_notification/", sse_stream_notification, name="sse_stream_notification"
    ),
]
