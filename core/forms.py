from django import forms
from .models import Tutorship, TimePeriod


class TutorshipForm(forms.ModelForm):
    description = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={"placeholder": "Descripción"}),
    )

    class Meta:
        model = Tutorship
        fields = ["name", "description"]


class TimePeriodForm(forms.ModelForm):
    class Meta:
        model = TimePeriod
        fields = ["start_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
