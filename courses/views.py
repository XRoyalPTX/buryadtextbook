from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Lesson, MyUser, CourseProgress, LessonProgress
from quizzes.models import Quiz
from social.models import Like
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .forms import CreateCourseForm, UpdateCourseForm, CreateLessonForm, UpdateLessonForm
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import F, Case, When, Value, BooleanField, Count, Max
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

# Create your views here.

def is_expert(user):
    if user.is_authenticated and (user.role == "expert" or user.is_superuser):
        return True
    return False


def courses(request):
    current_user = request.user
    courses = Course.objects.all()

    if not request.user.is_authenticated:
        return render(request, 'courses/courses.html', {'courses': courses})

    user_progress = CourseProgress.objects.filter(user=current_user)
    progress_dict = {p.course_id: p for p in user_progress}

    for course in courses:
        progress = progress_dict.get(course.id)
        
        if not progress:
            course.status = 'not_begun'
        elif progress.complete_date: 
            course.status = 'completed'
        else:
            course.status = 'begun'

    return render(request, 'courses/courses.html', context={
        'courses': courses,
    })


def open_course(request, course_id):
    current_course = get_object_or_404(Course, pk=course_id)
    lessons = Lesson.objects.filter(course=current_course, is_published=True).order_by('order_num')

    if not request.user.is_authenticated:
        return render(request, 'courses/course.html', context={
            'current_course': current_course,
            'lessons': lessons
        })

    is_course_begun = CourseProgress.objects.filter(course=current_course, user=request.user).exists()

    user_progress = LessonProgress.objects.filter(lesson__course=current_course, user=request.user)

    progress_dict = {lp.lesson_id: lp for lp in user_progress}

    for lesson in lessons:
        progress = progress_dict.get(lesson.id)
        if not progress:
            lesson.status = 'not_begun'
        elif progress.complete_date:
            lesson.status = 'completed'
        else:
            lesson.status = 'begun'

    course_progress = CourseProgress.objects.filter(course = current_course, user = request.user).first()

    if not course_progress:
        current_course.status = 'not_begun'
    elif course_progress.complete_date: 
        current_course.status = 'completed'
    else:
        current_course.status = 'begun'
        

    return render(request, 'courses/course.html', context={
        'current_course': current_course,
        'lessons': lessons,
        'is_course_begun': is_course_begun,
    })


@user_passes_test(is_expert)
def create_course(request, username):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            try:
                course.full_clean()
                course.save()
                messages.success(request, 'Курс успешно создан.')
                return redirect('studio_lessons', username=course.author.username, course_id=course.id)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = CreateCourseForm()

    return render(request, 'courses/create_course.html', {'form': form})


@user_passes_test(is_expert)
def update_course(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, pk=course_id)
    author_username = current_course.author.username
    if request.user == current_course.author or request.user.is_superuser:
        if request.method == 'POST':
            form = UpdateCourseForm(data=request.POST, instance=current_course)
            if form.is_valid():
                if form.has_changed():
                    current_course = form.save()
                    messages.success(request, 'Курс успешно отредактирован')
                    return redirect('studio_courses', username=author_username)
                else:
                    form.add_error(None, 'Вы не ввели никаких изменений')
        else:
            form = UpdateCourseForm(instance=current_course)
    else:
        raise PermissionDenied()
    
    return render(request, 'courses/update_course.html', {'form': form})
        


@user_passes_test(is_expert)
def delete_course(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
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

    if not CourseProgress.objects.filter(course=current_course, user=request.user).exists():
        messages.warning(request, "Для просмотра уроков необходимо начать прохождение курса.")
        return redirect('open_course', course_id=course_id)
    
    from social.models import Like, Comment
    user_liked = Like.objects.filter(user=request.user, lesson=current_lesson).exists()
    likes_cnt = Like.objects.filter(lesson=current_lesson).count()

    comments = Comment.objects.filter(lesson=current_lesson)
    comments_cnt = Comment.objects.filter(lesson=current_lesson).count()

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user, 
        lesson=current_lesson
    )

    is_lesson_completed = bool(progress.complete_date)

    prev_lesson = Lesson.objects.filter(
        course = current_course, 
        order_num__lt = current_lesson.order_num,
        is_published = True
    ).order_by('-order_num').first()
    
    next_lesson = Lesson.objects.filter(
        course = current_course, 
        order_num__gt = current_lesson.order_num,
        is_published = True
    ).order_by('order_num').first()

    return render(request, 'courses/lesson.html', {
        'current_course': current_course,
        'current_lesson': current_lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'is_lesson_completed': is_lesson_completed,
        'user_liked': user_liked,
        'likes_cnt': likes_cnt,
        'comments': comments,
        'comments_cnt': comments_cnt,
    })


@login_required
def create_lesson(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, pk=course_id)
    
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()

    if request.method == 'POST':
        form = CreateLessonForm(data=request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = current_course        
            lesson.save()
            messages.success(request, f'Урок №{lesson.order_num} успешно создан.')
            return redirect('studio_lessons', username=current_course.author.username, course_id=current_course.id) 
    else:
        form = CreateLessonForm()
    
    return render(request, 'courses/create_lesson.html', {
        'form': form,
        'current_course': current_course,
        'auto_order_num': current_course.get_next_lesson_number(),
    })


@user_passes_test(is_expert)
def update_lesson(request, username, course_id, lesson_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
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
                return redirect('studio_lessons', username=current_course.author.username, course_id=current_course.id) 
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
def delete_lesson(request, username, course_id, lesson_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, pk=lesson_id)
    deleted_order_num = current_lesson.order_num

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
            current_course.lessons.filter(
                order_num__gt=deleted_order_num
            ).update(order_num=F('order_num') - 1)
            return response
        
    return HttpResponse(status=204) 


@user_passes_test(is_expert)
def studio_courses(request, username):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    needed_user = get_object_or_404(MyUser, username=username)
    courses = Course.objects.filter(author=needed_user).annotate(
        lessons_count=Count('lessons'),
    ).order_by('id')

    total_quizzes_count = Quiz.objects.filter(lesson__course__author=needed_user).count()
    total_like_count = Like.objects.filter(lesson__course__author=needed_user).count()

    return render(request, 'courses/studio_courses.html', context={
        'courses': courses,
        'author_user': needed_user,
        'total_quizzes_count': total_quizzes_count,
        'total_like_count': total_like_count
    })

@user_passes_test(is_expert)
def studio_lessons(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    needed_user = get_object_or_404(MyUser, username=username)
    current_course = get_object_or_404(Course, pk=course_id, author=needed_user)
    lessons = current_course.lessons.all().annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    ).order_by('order_num')

    return render(request, 'courses/studio_lessons.html', context={
        'current_course': current_course,
        'lessons': lessons,
    })


@user_passes_test(is_expert)
def change_order_number(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, pk=course_id)
    lessons = current_course.lessons

    if request.user == current_course.author or request.user.is_superuser:
        list_id = request.POST.getlist('order[]')

        for lesson_id in list_id:
            lessons.filter(pk=lesson_id).update(order_num=F('order_num') + 1000)

        for new_order_num, lesson_id in enumerate(list_id, start=1):
            lessons.filter(pk=lesson_id).update(order_num=new_order_num)

        return HttpResponse(status=204)
    else:
        raise PermissionDenied()


@user_passes_test(is_expert)
def publish_course(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_author = get_object_or_404(MyUser, username=username)
    current_course = get_object_or_404(Course, pk=course_id, author=current_author)
    current_course.lessons_count = current_course.lessons.count()

    success_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-success">Курс успешно опубликован.</div>
        </div>
    '''
    error_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-danger">Курс не может быть опубликован, так как он не содержит ни одного опубликованного урока.</div>
        </div>
    '''

    if request.user != current_author and not request.user.is_superuser:
        raise PermissionDenied()

    if request.method == 'POST':
        current_course.is_published = True
        current_course.save()

        if not current_course.is_published:
            card_html = render_to_string('courses/course_card.html', {'card': current_course}, request=request)
            return HttpResponse(card_html + error_message)
        else:
            card_html = render_to_string('courses/course_card.html', {'card': current_course}, request=request)
            return HttpResponse(card_html + success_message)
        

@user_passes_test(is_expert)
def unpublish_course(request, username, course_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_author = get_object_or_404(MyUser, username=username)
    current_course = get_object_or_404(Course, pk=course_id, author=current_author)
    current_course.lessons_count = current_course.lessons.count()

    if request.user != current_author and not request.user.is_superuser:
        raise PermissionDenied()
    
    success_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-success">Курс успешно добавлен в черновик.</div>
        </div>
    '''

    if request.method == 'POST':
        current_course.is_published = False
        current_course.save()
        card_html = render_to_string('courses/course_card.html', {'card': current_course}, request=request)
        return HttpResponse(card_html + success_message)


@user_passes_test(is_expert)
def publish_lesson(request, username, course_id, lesson_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_author = get_object_or_404(MyUser, username=username)
    current_course = get_object_or_404(Course, pk=course_id, author=current_author)
    current_lesson = get_object_or_404(Lesson, pk=lesson_id, course=current_course)

    if request.user != current_author and not request.user.is_superuser:
        raise PermissionDenied()
    
    success_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-success">Урок успешно опубликован.</div>
        </div>
    '''
    
    if request.method == 'POST':
        current_lesson.is_published = True
        current_lesson.save()
        CourseProgress.objects.filter(
            course=current_course, 
            complete_date__isnull=False
        ).update(complete_date=None)
        card_html = render_to_string('courses/lesson_card.html', {'card': current_lesson, 'current_course': current_course}, request=request)
        return HttpResponse(card_html + success_message)
    

@user_passes_test(is_expert)
def unpublish_lesson(request, username, course_id, lesson_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_author = get_object_or_404(MyUser, username=username)
    current_course = get_object_or_404(Course, pk=course_id, author=current_author)
    current_lesson = get_object_or_404(Lesson, pk=lesson_id, course=current_course)

    if request.user != current_author and not request.user.is_superuser:
        raise PermissionDenied()
    
    success_message = '''
        <div id="id_messages-container" class="messages-container" hx-swap-oob="true">
            <div class="alert alert-success">Урок успешно добавлен в черновик.</div>
        </div>
    '''
    
    if request.method == 'POST':
        current_lesson.is_published = False
        current_lesson.save()
        card_html = render_to_string('courses/lesson_card.html', {'card': current_lesson, 'current_course': current_course}, request=request)
        return HttpResponse(card_html + success_message)
    


@login_required
def create_course_progress(request, course_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_user = request.user
    first_lesson = current_course.lessons.filter(
        course = current_course,
        is_published = True,
    ).order_by('order_num').first()

    progress, created = CourseProgress.objects.get_or_create(course=current_course, user=current_user)

    messages.success(request, 'Вы успешно записались на курс! Добро пожаловать на первый урок текущего курса.')

    return redirect('open_lesson', course_id, first_lesson.order_num)


@login_required
def complete_lesson(request, course_id, lesson_order_num):
    current_course = get_object_or_404(Course, pk=course_id)
    current_user = request.user
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    
    # Получаем прогресс текущего урока
    current_lesson_progress = LessonProgress.objects.filter(
        user=current_user, 
        lesson=current_lesson
    ).first()

    today = timezone.now().date()

    if request.method == 'POST':
        if not current_lesson_progress.complete_date:
            current_lesson_progress.complete_date = timezone.now()
            current_lesson_progress.save()

            published_lessons_count = current_course.lessons.filter(is_published=True).count()
            
            completed_lessons_count = LessonProgress.objects.filter(
                user=current_user,
                lesson__course=current_course,
                lesson__is_published=True,
                complete_date__isnull=False
            ).count()

            if published_lessons_count == completed_lessons_count:
                current_course_progress = CourseProgress.objects.filter(
                    user=current_user,
                    course=current_course
                ).first()

                if current_course_progress and not current_course_progress.complete_date:
                    current_course_progress.complete_date = timezone.now()
                    current_course_progress.save()
                    messages.success(request, 'Поздравляем! Вы полностью прошли курс!')

            if current_user.streak_count == 0:
                current_user.last_activity_date = today
                current_user.streak_count = 1
                current_user.save()
            elif current_user.streak_count > 0 and current_user.last_activity_date == today - timedelta(days=1):
                current_user.last_activity_date = today
                current_user.streak_count += 1
                current_user.save()
            elif current_user.streak_count > 0 and current_user.last_activity_date < today - timedelta(days=1):
                current_user.last_activity_date = today
                current_user.streak_count = 1
                current_user.save()

            messages.success(request, 'Урок отмечен пройденным.')
        else:
            messages.info(request, 'Вы уже проходили этот урок ранее.')

        return redirect('open_lesson', course_id, lesson_order_num)