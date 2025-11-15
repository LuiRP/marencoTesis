from django.shortcuts import render
from django.contrib import messages


# Create your views here.
def index(request):
    messages.success(request, "Hola")
    messages.info(request, "Hola")
    messages.warning(request, "Hola")
    messages.error(request, "Hola")
    return render(request, "index.html")
