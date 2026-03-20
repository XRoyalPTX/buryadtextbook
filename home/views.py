from django.shortcuts import render, redirect
from django.utils import timezone

# Create your views here.


def home(request):
    return render(request, "home/homepage.html", context=None)


def about(request):
    return render(request, "home/about.html", context=None)
