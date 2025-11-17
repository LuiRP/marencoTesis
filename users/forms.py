from django import forms
from .models import Review


class ExpandedSignUpForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={"placeholder": "Nombre"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Apellido",
        widget=forms.TextInput(attrs={"placeholder": "Apellido"}),
    )
    is_tutor = forms.BooleanField(required=False, label="Tutor")
    field_order = [
        "first_name",
        "last_name",
        "email",
        "password1",
        "password2",
        "is_tutor",
    ]

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_tutor = self.cleaned_data["is_tutor"]
        user.save()


class ReviewForm(forms.ModelForm):
    body = forms.CharField(
        label="Cuerpo de la reseña",
        widget=forms.Textarea(attrs={"placeholder": "Cuerpo de la reseña"}),
    )

    rating = forms.IntegerField(
        label="Calificación",
        max_value=5,
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "Calificación"}),
    )

    class Meta:
        model = Review
        fields = ["body", "rating"]
