from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Lesson
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .forms import CreateCourseForm, UpdateCourseForm
from django.core.exceptions import ValidationError, PermissionDenied

# Create your views here.

def is_expert(user):
    if user.is_authenticated and (user.role == "expert" or user.is_superuser):
        return True
    return False


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


@user_passes_test(is_expert)
def create_course(request):
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            try:
                course.full_clean()
                course.save()
                messages.success(request, 'Курс успешно создан.')
                return redirect('courses')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = CreateCourseForm()

    return render(request, 'courses/create_course.html', {'form': form})


@user_passes_test(is_expert)
def update_course(request, course_id):
    current_course = get_object_or_404(Course, pk=course_id)
    if request.user == current_course.author or request.user.is_superuser:
        if request.method == 'POST':
            form = UpdateCourseForm(data=request.POST, instance=current_course)
            if form.is_valid():
                if form.has_changed():
                    current_course = form.save()
                    messages.success(request, 'Курс успешно отредактирован')
                    return redirect('courses')
                else:
                    form.add_error(None, 'Вы не ввели никаких изменений')
        else:
            form = UpdateCourseForm(instance=current_course)
    else:
        raise PermissionDenied()
    
    return render(request, 'courses/update_course.html', {'form': form})
        


@user_passes_test(is_expert)
def delete_course(request, course_id):
    current_course = get_object_or_404(Course, pk=course_id)
    success_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-success">Курс успешно удален.</div>
        </div>
    '''
    error_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-error">У вас нет прав для удаления этого курса.</div>
        </div>
    '''

    if request.user != current_course.author and not request.user.is_superuser:
        response = HttpResponse(error_message)
        response['HX-Reswap'] = 'none'
        return response

    if request.method == 'POST':
        current_course.delete()
        return HttpResponse(success_message)
    
    return HttpResponse()