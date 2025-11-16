from django import forms
from .models import Tutorship


class TutorshipForm(forms.ModelForm):
    class Meta:
        model = Tutorship
        fields = ["name", "description"]
