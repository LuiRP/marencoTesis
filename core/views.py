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
from django.db.models import Q
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError


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
    paginator = Paginator(tutorships, 2)
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
def timetable(request):
    periods = TimePeriod.objects.filter(tutor=request.user).order_by("start_time")
    periods_by_day = {}
    for day_code, day_name in WEEK_DAYS:
        periods_by_day[day_code] = periods.filter(week_day=day_code)

    context = {"week_days": WEEK_DAYS, "periods_by_day": periods_by_day}
    if not request.user.is_tutor:
        return render(request, "timetable/index_student.html", context)
    else:
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
                return redirect(reverse("timetable"))

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
    except TimePeriod.DoesNotExist:
        messages.error(
            request, "El periodo no existe o no tienes permisos para editarlo."
        )
        return redirect(reverse("timetable"))

    if request.method == "POST":
        form = TimePeriodForm(request.POST, instance=period)
        if form.is_valid():
            try:
                updated_period = form.save(commit=False)
                updated_period.save()

                messages.success(request, "Periodo actualizado exitosamente.")
                return redirect(reverse("timetable"))

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
        period.delete()
        messages.success(request, "Periodo eliminado exitosamente.")
    except TimePeriod.DoesNotExist:
        messages.error(
            request, "El periodo no existe o no tienes permisos para eliminarlo."
        )

    return redirect(reverse("timetable"))
