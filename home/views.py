from django.shortcuts import render
from django.utils import timezone

# Create your views here.


def home(request):
    time = timezone.now()
    return render(request, "home/homepage.html", context={
        "time": time,
    })
