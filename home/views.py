from django.shortcuts import render, redirect
from django.utils import timezone

# Create your views here.


def home(request):
    return render(request, "home/homepage.html", context=None)


def about(request):
    return render(request, "home/about.html", context=None)


def under_construction(request):
    previous_url = request.META.get('HTTP_REFERER', '/')

    context = {
        'previous_url': previous_url,
    }
    return render(request, 'home/under_construction.html', context)