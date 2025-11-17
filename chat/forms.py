from django import forms
from .models import Message


class ChatForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
