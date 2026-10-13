from django.shortcuts import render, redirect
from django.utils import timezone

# Create your views here.


def home(request):
    return render(request, "home/homepage.html", context=None)


def about(request):
    return render(request, "home/about.html", context=None)


from django.utils.http import url_has_allowed_host_and_scheme


def under_construction(request):
    previous_url = request.META.get('HTTP_REFERER', '/')
    allowed_hosts = {request.get_host()}
    if not url_has_allowed_host_and_scheme(previous_url, allowed_hosts=allowed_hosts, require_https=request.is_secure()):
        previous_url = '/'

    context = {
        'previous_url': previous_url,
    }
    return render(request, 'home/under_construction.html', context)


def confidential(request):
    return render(request, 'home/confidential.html', context=None)


def agreement(request):
    return render(request, 'home/agreement.html', context=None)