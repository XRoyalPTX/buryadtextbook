from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course
from django.http import Http404

# Create your views here.


@login_required
def courses(request):
    user = request.user
    courses = Course.objects.all()
    return render(request, 'courses/courses.html', context={
        'courses': courses,
    })

@login_required
def open_course(request, course_id):
    try:
        current_course = Course.objects.get(pk=course_id)
    except:
        raise Http404("Course does not exist")
    return render(request, 'courses/course.html', context={
        'current_course': current_course,
    })

