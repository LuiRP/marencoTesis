from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied, BadRequest
from django.core.paginator import Paginator
from .forms import TutorshipForm, TimePeriodForm
from .models import Tutorship, TimePeriod
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q, Max, Count, F, Subquery, OuterRef
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from notifications import models as NotificationModels
from chat import models as ChatModels
from django.http import JsonResponse


# Create your views here.
@login_required
def index(request):
    return render(request, "index.html")


@login_required
def tutorships(request):
    search_query = request.GET.get("search", "")
    show_my_tutorships = request.GET.get("my_tutorships") == "on"
    tutorships = Tutorship.objects.all().order_by("-created_at")
    if show_my_tutorships:
        tutorships = tutorships.filter(tutor=request.user)
    if search_query:
        tutorships = tutorships.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    paginator = Paginator(tutorships, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "tutorships/index.html", context)


@login_required
def tutorship_create(request):
    if not request.user.is_tutor:
        raise PermissionDenied()

    if request.method == "POST":
        form = TutorshipForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            tutor = request.user
            r = Tutorship(name=name, tutor=tutor, description=description)
            r.save()
            messages.success(request, "Tutoria creada exitosamente.")
            return redirect(reverse("tutorships"))
    else:
        form = TutorshipForm()
    context = {"form": form}
    return render(request, "tutorships/create.html", context)


@login_required
def tutorship_update(request, tutorship_id):
    tutorship = get_object_or_404(Tutorship, pk=tutorship_id)
    if tutorship.tutor != request.user:
        raise PermissionDenied()
    if request.method == "POST":
        form = TutorshipForm(request.POST, instance=tutorship)
        if form.is_valid():
            tutorship = form.save()
            messages.success(request, "Tutoria actualizada exitosamente.")
            return redirect(reverse("tutorships"))
    else:
        form = TutorshipForm(instance=tutorship)
    context = {"form": form}
    return render(request, "tutorships/update.html", context)


@login_required
def tutorship_delete(request, tutorship_id):
    tutorship = get_object_or_404(Tutorship, pk=tutorship_id)
    if tutorship.tutor != request.user:
        raise PermissionDenied()
    if request.method == "POST":
        tutorship.delete()
        messages.success(request, "Tutoria eliminada exitosamente.")
        return redirect(reverse("tutorships"))
    return render(request, "tutorships/delete.html")


WEEK_DAYS = [
    ("lunes", "Lunes"),
    ("martes", "Martes"),
    ("miercoles", "Miercoles"),
    ("jueves", "Jueves"),
    ("viernes", "Viernes"),
    ("sabado", "Sabado"),
    ("domingo", "Domingo"),
]


@login_required
def timetable(request, user_id):
    if user_id == request.user.pk:
        if request.user.is_tutor:
            periods = TimePeriod.objects.filter(tutor=user_id).order_by("start_time")
        else:
            periods = TimePeriod.objects.filter(student=user_id).order_by("start_time")
    else:
        periods = TimePeriod.objects.filter(tutor=user_id).order_by("start_time")
    periods_by_day = {}
    for day_code, day_name in WEEK_DAYS:
        periods_by_day[day_code] = periods.filter(week_day=day_code)

    context = {"week_days": WEEK_DAYS, "periods_by_day": periods_by_day}
    return render(request, "timetable/index_tutor.html", context)


@login_required
def create_timetable(request, week_day):
    if not request.user.is_tutor:
        raise PermissionDenied()
    week_days_dict = dict(WEEK_DAYS)
    if not week_day in week_days_dict.keys():
        raise BadRequest()
    if not request.user.is_tutor:
        raise PermissionDenied()

    if request.method == "POST":
        form = TimePeriodForm(request.POST)
        if form.is_valid():
            try:
                period = form.save(commit=False)
                period.week_day = week_day
                period.tutor = request.user
                period.save()

                messages.success(request, "Periodo creado exitosamente.")
                return redirect(reverse("timetable", args=[request.user.pk]))

            except ValidationError as e:
                error_message = " ".join(e.messages)
                messages.error(request, error_message)

    else:
        form = TimePeriodForm()
    context = {"day": (week_day, week_days_dict[week_day]), "form": form}
    return render(request, "timetable/create.html", context)


@login_required
def edit_timetable(request, period_id):
    try:
        period = TimePeriod.objects.get(id=period_id, tutor=request.user)
        if period.student:
            messages.error(
                request,
                "No puedes editar un periodo que ya tiene un estudiante asignado.",
            )
            return redirect(reverse("timetable", args=[request.user.pk]))
    except TimePeriod.DoesNotExist:
        messages.error(
            request, "El periodo no existe o no tienes permisos para editarlo."
        )
        return redirect(reverse("timetable", args=[request.user.pk]))

    if request.method == "POST":
        form = TimePeriodForm(request.POST, instance=period)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Periodo actualizado exitosamente.")
                return redirect(reverse("timetable", args=[request.user.pk]))

            except ValidationError as e:
                error_message = " ".join(e.messages)
                messages.error(request, error_message)
    else:
        form = TimePeriodForm(instance=period)

    week_days_dict = dict(WEEK_DAYS)
    context = {
        "form": form,
        "period": period,
        "day": (period.week_day, week_days_dict.get(period.week_day, "")),
    }
    return render(request, "timetable/edit.html", context)


@login_required
def delete_timetable(request, period_id):
    try:
        period = TimePeriod.objects.get(id=period_id, tutor=request.user)
        if period.student:
            messages.error(
                request,
                "No puedes eliminar un periodo que ya tiene un estudiante asignado.",
            )
        else:
            period.delete()
            messages.success(request, "Periodo eliminado exitosamente.")
    except TimePeriod.DoesNotExist:
        messages.error(
            request, "El periodo no existe o no tienes permisos para eliminarlo."
        )
    return redirect(reverse("timetable", args=[request.user.pk]))


@login_required
def add_student(request, period_id):
    if request.user.is_tutor:
        raise PermissionDenied()
    try:
        period = TimePeriod.objects.get(id=period_id)
        if period.student:
            messages.error(request, "Este periodo ya está reservado.")
        else:
            period.student = request.user
            period.save()
            messages.success(request, "Periodo reservado exitosamente.")
            notification = NotificationModels.Notification(
                type="reserva",
                body="ha reservado un periodo",
                action_user=request.user,
                receiver=period.tutor,
            )
            notification.save()

    except TimePeriod.DoesNotExist:
        messages.error(request, "El periodo no existe.")
    return redirect(reverse("timetable", args=[period.tutor.pk]))


@login_required
def remove_student(request, period_id):
    try:
        period = TimePeriod.objects.get(id=period_id)

        if request.user != period.tutor and request.user != period.student:
            raise PermissionDenied()

        if not period.student:
            messages.error(request, "Este periodo no está reservado.")
        else:
            period.student = None
            period.save()
            messages.success(request, "Reserva eliminada exitosamente.")

    except TimePeriod.DoesNotExist:
        messages.error(request, "El periodo no existe.")

    if request.user.is_tutor:
        return redirect(reverse("timetable", args=[period.tutor.pk]))
    else:
        return redirect(reverse("timetable", args=[request.user.pk]))


@login_required
def get_unread_count(request):
    current_user = request.user
    unread_count = (
        ChatModels.ChatThread.objects.filter(
            Q(user1=current_user) | Q(user2=current_user)
        ).aggregate(
            total_unread=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=current_user),
            )
        )[
            "total_unread"
        ]
        or 0
    )

    return JsonResponse({"unread_count": unread_count})


@login_required
def get_unread_count_notifications(request):
    current_user = request.user
    unread_count = NotificationModels.Notification.objects.filter(
        receiver=current_user, is_read=False
    ).count()

    return JsonResponse({"unread_count": unread_count})
