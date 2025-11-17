from django.core.paginator import Paginator
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import CustomUser, Review
from .forms import ReviewForm
from notifications import models as NotificationModels
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg


# Create your views here.
@login_required
def profile(request, user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        raise Http404("No se encuentra el usuario.")

    reviews = Review.objects.filter(reviewed=user)
    ratings = list(reviews.values_list("rating", flat=True))
    if ratings:
        reviews_avg_rating = (
            reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        )
        stars = get_star_list(reviews_avg_rating)
    else:
        reviews_avg_rating = 0
        stars = [0, 0, 0, 0, 0]
    if not reviews.exists():
        there_is_ratings = False
    else:
        there_is_ratings = True
    context = {
        "user": user,
        "avg_rating": reviews_avg_rating,
        "stars": stars,
        "there_is_ratings": there_is_ratings,
    }
    return render(request, "profile/index.html", context)


@login_required
def reviews(request, user_id):
    reviewed = get_object_or_404(CustomUser, pk=user_id)
    reviews = Review.objects.filter(reviewed=reviewed).order_by("-created_at")
    paginator = Paginator(reviews, 2)

    reviews_count = reviews.count()

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    for review in page_obj:
        review.stars = get_star_list(review.rating)
    context = {
        "page_obj": page_obj,
        "reviews_count": reviews_count,
        "user_id": user_id,
    }
    return render(request, "reviews/index.html", context)


@login_required
def review_create(request, user_id):
    if request.user.pk == user_id:
        raise PermissionDenied()
    reviewed = get_object_or_404(CustomUser, pk=user_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"]
            rating = form.cleaned_data["rating"]
            author = request.user
            r = Review(body=body, author=author, rating=rating, reviewed=reviewed)
            r.save()
            messages.success(request, "Reseña creada exitosamente.")
            notifification = NotificationModels.Notification(
                type="reseña",
                body="ha escrito una reseña",
                action_user=request.user,
                receiver=reviewed,
            )
            notifification.save()
            redirect_url = reverse("reviews", kwargs={"user_id": reviewed.pk})
            return HttpResponseRedirect(redirect_url)
    else:
        form = ReviewForm()
    context = {"form": form}
    return render(request, "reviews/create.html", context)


@login_required
def review_update(request, user_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    reviewed_id = review.reviewed.pk
    if review.author != request.user:
        raise PermissionDenied()
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save()
            messages.success(request, "Reseña actualizada exitosamente.")
            redirect_url = reverse("reviews", kwargs={"user_id": reviewed_id})
            return HttpResponseRedirect(redirect_url)
    else:
        form = ReviewForm(instance=review)
    context = {"form": form}
    return render(request, "reviews/update.html", context)


@login_required
def review_delete(request, user_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    reviewed_id = review.reviewed.pk
    if review.author != request.user:
        raise PermissionDenied()
    if request.method == "POST":
        review.delete()
        messages.success(request, "Reseña eliminada exitosamente.")
        redirect_url = reverse("reviews", kwargs={"user_id": reviewed_id})
        return HttpResponseRedirect(redirect_url)
    return render(request, "reviews/delete.html")


def get_star_list(rating):
    stars = []
    full_stars = int(rating)
    has_half_star = (rating - full_stars) >= 0.5

    for i in range(full_stars):
        stars.append(1)

    if has_half_star:
        stars.append(0.5)

    empty_stars = 5 - len(stars)
    for i in range(empty_stars):
        stars.append(0)

    return stars
