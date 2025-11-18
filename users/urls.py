from django.urls import path, include
from .views import (
    profile,
    reviews,
    review_create,
    review_update,
    review_delete,
    options,
    account_basic,
)

urlpatterns = [
    path("profile/<int:user_id>/", profile, name="profile"),
    path("profile/<int:user_id>/reviews/", reviews, name="reviews"),
    path("profile/<int:user_id>/reviews/create", review_create, name="review_create"),
    path(
        "profile/<int:user_id>/reviews/edit/<int:review_id>",
        review_update,
        name="review_update",
    ),
    path(
        "profile/<int:user_id>/reviews/delete/<int:review_id>",
        review_delete,
        name="review_delete",
    ),
    path("accounts/", options, name="options"),
    path("accounts/basic_information", account_basic, name="account_basic"),
]
