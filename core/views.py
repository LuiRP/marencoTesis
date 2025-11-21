from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .forms import TutorshipForm
from .models import Tutorship, TimePeriod
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q


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


def timetable(request):
    if not request.user.is_tutor:
        raise PermissionDenied()
    return render(request, "timetable/index_tutor.html")


def create_timetable(request):
    WEEK_DAYS = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miercoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
        ("sabado", "Sabado"),
        ("domingo", "Domingo"),
    ]
    if not request.user.is_tutor:
        raise PermissionDenied()

    context = {"week_days": WEEK_DAYS}
    return render(request, "timetable/create.html", context)
