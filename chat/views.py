from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Max, Count, F, Subquery, OuterRef
from .models import ChatThread, Message
from .forms import ChatForm
from notifications import models as NotificationModels

CustomUser = get_user_model()


# Create your views here.
@login_required
def inbox(request):
    current_user = request.user
    search_query = request.GET.get("search", "")
    recent_threads = (
        ChatThread.objects.filter(Q(user1=current_user) | Q(user2=current_user))
        .annotate(
            last_message_time=Max("messages__timestamp"),
            last_message_content=Subquery(
                Message.objects.filter(thread=OuterRef("pk"))
                .order_by("-timestamp")
                .values("content")[:1]
            ),
            total_messages=Count("messages"),
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=current_user),
            ),
        )
        .order_by(
            F("last_message_time").desc(nulls_last=True),
            "-id",
        )
    )

    if search_query:
        recent_threads = recent_threads.filter(
            Q(user1__first_name__icontains=search_query)
            | Q(user1__last_name__icontains=search_query)
            | Q(user1__email__icontains=search_query)
            | Q(user2__first_name__icontains=search_query)
            | Q(user2__last_name__icontains=search_query)
            | Q(user2__email__icontains=search_query)
        )

    for thread in recent_threads:
        thread.other_user = (
            thread.user2 if thread.user1 == current_user else thread.user1
        )
    paginator = Paginator(recent_threads, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "chat/index.html", context)


@login_required
def get_or_create_chat_thread(request, other_user_id):
    current_user = request.user
    other_user = get_object_or_404(CustomUser, id=other_user_id)

    if current_user == other_user:
        return redirect("inbox")

    try:
        thread = ChatThread.objects.get(
            Q(user1=current_user, user2=other_user)
            | Q(user1=other_user, user2=current_user)
        )
    except ChatThread.DoesNotExist:
        if current_user.id < other_user.id:
            thread = ChatThread.objects.create(user1=current_user, user2=other_user)
        else:
            thread = ChatThread.objects.create(user1=other_user, user2=current_user)

    thread.messages.filter(sender=other_user, is_read=False).update(is_read=True)

    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            chat_message = Message(content=content, sender=request.user, thread=thread)
            chat_message.save()

            notification = NotificationModels.Notification(
                type="mensaje",
                body="ha escrito un mensaje",
                action_user=request.user,
                receiver=other_user,
            )
            notification.save()
    else:
        form = ChatForm()

    chat_messages = thread.messages.all()

    context = {
        "thread": thread,
        "other_user": other_user,
        "chat_messages": chat_messages,
    }
    return render(request, "chat/chat.html", context)
