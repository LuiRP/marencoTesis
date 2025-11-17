from django import forms
from .models import Tutorship


class TutorshipForm(forms.ModelForm):
    description = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={"placeholder": "Descripción"}),
    )

    class Meta:
        model = Tutorship
        fields = ["name", "description"]
