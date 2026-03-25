from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# Create your views here.


def courses(request):
    user = request.user
    courses = Course.objects.all()
    return render(request, 'courses/courses.html', context={
        'courses': courses,
    })


@login_required
def open_course(request, course_id):
    current_course = get_object_or_404(Course, pk=course_id)
    lessons = Lesson.objects.filter(course=current_course).order_by('order_num')

    return render(request, 'courses/course.html', context={
        'current_course': current_course,
        'lessons': lessons,
    })

