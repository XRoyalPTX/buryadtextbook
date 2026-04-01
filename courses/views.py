from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Lesson, MyUser
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .forms import CreateCourseForm, UpdateCourseForm, CreateLessonForm, UpdateLessonForm
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Count, Max

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


@login_required
def open_lesson(request, course_id, lesson_order_num):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    number = current_course.lessons.count()

    prev_lesson = Lesson.objects.filter(
        course=current_course, 
        order_num__lt=current_lesson.order_num
    ).order_by('-order_num').first()
    
    next_lesson = Lesson.objects.filter(
        course=current_course, 
        order_num__gt=current_lesson.order_num
    ).order_by('order_num').first()

    return render(request, 'courses/lesson.html', {
        'current_course': current_course,
        'current_lesson': current_lesson,
        'num_of_lessons': number,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    })


def get_next_order_num(current_course):
    used_numbers = list(current_course.lessons.values_list('order_num', flat=True).order_by('order_num'))
    missed_numbers = []

    if not used_numbers:
        return [1]
    
    if used_numbers[0] != 1:
        gap = range(1, used_numbers[0])
        missed_numbers.extend(gap)

    for i in range(len(used_numbers) - 1):
        if used_numbers[i] + 1 != used_numbers[i+1]:
            gap = range(used_numbers[i] + 1, used_numbers[i+1])
            missed_numbers.extend(gap)
    
    if missed_numbers:
        return missed_numbers
            
    return [len(used_numbers) + 1]


@user_passes_test(is_expert)
def create_lesson(request, course_id):
    current_course = get_object_or_404(Course, pk=course_id)
    
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    free_numbers = get_next_order_num(current_course)
    auto_order_num = free_numbers[0]

    if request.method == 'POST':
        form = CreateLessonForm(data=request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = current_course
            
            lesson.order_num = free_numbers[0] 
            
            lesson.save()
            messages.success(request, f'Урок №{lesson.order_num} успешно создан.')
            return redirect('open_course', course_id=current_course.id) 
    else:
        form = CreateLessonForm()
    
    return render(request, 'courses/create_lesson.html', {
        'form': form,
        'current_course': current_course,
        'auto_order_num': auto_order_num,
    })


@user_passes_test(is_expert)
def update_lesson(request, course_id, lesson_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, course=current_course, pk=lesson_id)
    lesson_order_num = current_lesson.order_num

    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()

    if request.method == 'POST':
        form = UpdateLessonForm(data=request.POST, instance=current_lesson)
        if form.is_valid():
            if form.has_changed():
                current_lesson = form.save()
                messages.success(request, f'Урок №{current_lesson.order_num} успешно изменен.')
                return redirect('open_course', course_id=current_course.id) 
            else:
                form.add_error(None, 'Вы не ввели никаких изменений')

    else:
        form = UpdateLessonForm(instance=current_lesson)
    
    return render(request, 'courses/update_lesson.html', {
        'form': form,
        'current_course': current_course,
        'order_num': lesson_order_num,
    })


@user_passes_test(is_expert)
def delete_lesson(request, course_id, lesson_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, pk=lesson_id)

    success_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-success">Урок успешно удален.</div>
        </div>
    '''
    error_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-error">У вас нет прав для удаления этого урока.</div>
        </div>
    '''

    if request.user != current_course.author and not request.user.is_superuser:
        response = HttpResponse(error_message)
        response['HX-Reswap'] = 'none'
        return response
    
    if request.method == 'POST':
        if current_lesson.course == current_course:
            response = HttpResponse(success_message)
            current_lesson.delete()
            return response
        
    return HttpResponse(status=204) 


@user_passes_test(is_expert)
def studio_courses(request, username):
    needed_user = get_object_or_404(MyUser, username=username)
    courses = Course.objects.filter(author=needed_user).annotate(
        lessons_count=Count('lessons'),
        max_lesson=Max('lessons__order_num')
    )
    return render(request, 'courses/studio_courses.html', context={
        'courses': courses,
        'author_user': needed_user,
    })
