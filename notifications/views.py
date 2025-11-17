from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
import json, asyncio
from django.core.cache import cache
from .models import Notification
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator


@login_required
def notifications(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by(
        "-created_at"
    )
    paginator = Paginator(notifications, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "notifications/index.html", context)


async def get_user_id(request):
    return await sync_to_async(lambda: request.user.id)()


async def sse_stream_notification(request):
    user_id = await get_user_id(request)

    async def event_stream():
        sent_notification_ids = set()

        while True:
            cache_key = f"user_{user_id}_notifications"
            user_notifications = cache.get(cache_key, [])

            for notification in user_notifications:
                if notification["id"] not in sent_notification_ids:
                    toast_html = create_toast_html(notification)
                    yield f"data: {json.dumps({'html': toast_html})}\n\n"
                    sent_notification_ids.add(notification["id"])

            await cleanup_old_notifications(
                cache_key, sent_notification_ids, user_notifications
            )

            await asyncio.sleep(2)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["Connection"] = "keep-alive"
    return response


def create_toast_html(notification):
    return f"""
    <div class="toast align-items-center bg-info text-white border-0 m-2" 
         role="alert" 
         aria-live="assertive" 
         aria-atomic="true">
        <div class="d-flex">
            <div class="toast-body">
                Ha recibido una notificación
            </div>
            <button type="button" 
                    class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" 
                    aria-label="Close"></button>
        </div>
    </div>
    """


def cleanup_old_notifications_sync(cache_key, sent_ids, current_notifications):
    remaining = [n for n in current_notifications if n["id"] not in sent_ids]
    cache.set(cache_key, remaining, timeout=300)


cleanup_old_notifications = sync_to_async(cleanup_old_notifications_sync)
