from django.shortcuts import render, redirect
from django.http import Http404
from django.views.decorators.http import require_POST
from courses.models import Course, Lesson, LessonProgress, CourseProgress
from .models import Quiz, Question, QuizProgress
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import QuizForm, QuestionForm, AnswerFormSet
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext as _


# Create your views here.

def is_expert(user):
    if user.is_authenticated and (user.role == "expert" or user.is_superuser):
        return True
    return False


@login_required
def open_quiz(request, course_id, lesson_order_num, quiz_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    current_quiz = get_object_or_404(Quiz, pk=quiz_id, lesson=current_lesson)

    # Проверка публикации и прав доступа
    is_owner_or_admin = (request.user == current_course.author or request.user.is_superuser)
    if not is_owner_or_admin:
        if not current_course.is_published or not current_lesson.is_published:
            raise Http404(_("Тест не найден."))
        if not CourseProgress.objects.filter(course=current_course, user=request.user).exists():
            messages.warning(request, _("Для прохождения теста необходимо начать курс."))
            return redirect('open_course', course_id=course_id)

    if request.method == 'POST':
        from .models import QuizProgress
        progress, created = QuizProgress.objects.get_or_create(
            user=request.user, 
            quiz=current_quiz
        )
        
        user_answers = {}
        for question in current_quiz.questions.all():
            answer_ids = request.POST.getlist(f'question_{question.id}')
            user_answers[str(question.id)] = answer_ids
            
        progress.calculate_and_save_result(user_answers)
        
        if progress.is_passed:
            lesson_progress, _created = LessonProgress.objects.get_or_create(
                user=request.user, 
                lesson=current_lesson
            )
            
            if not lesson_progress.complete_date:
                today = timezone.now().date()
                lesson_progress.complete_date = timezone.now()
                lesson_progress.save()

                published_lessons_count = current_course.lessons.filter(is_published=True).count()
                
                completed_lessons_count = LessonProgress.objects.filter(
                    user=request.user,
                    lesson__course=current_course,
                    lesson__is_published=True,
                    complete_date__isnull=False
                ).count()

                if published_lessons_count == completed_lessons_count:
                    current_course_progress = CourseProgress.objects.filter(
                        user=request.user,
                        course=current_course
                    ).first()

                    if current_course_progress and not current_course_progress.complete_date:
                        current_course_progress.complete_date = timezone.now()
                        current_course_progress.save()
                        messages.success(request, _('Поздравляем! Вы полностью прошли курс!'))

                current_user = request.user
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

                messages.success(request, _('Тест пройден, урок отмечен пройденным.'))
            else:
                messages.success(request, _('Тест пройден.'))
        
        return redirect('quiz_result', course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=current_quiz.id, progress_id=progress.id)

    return render(request, 'quizzes/quiz.html', {
        'current_course': current_course,
        'current_lesson': current_lesson,
        'current_quiz': current_quiz,
    })

@user_passes_test(is_expert)
def create_quiz(request, username, course_id, lesson_order_num):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()

    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    
    if hasattr(current_lesson, 'quiz'):
        return redirect('update_quiz', username=request.user.username, course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=current_lesson.quiz.id) 

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = current_lesson 
            quiz.save()
            messages.success(request, _('Тест успешно создан.'))
            return redirect('open_quiz_builder', username=request.user.username, course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'quizzes/create_quiz.html', {
        'form': form,
        'current_lesson': current_lesson,
    })


@user_passes_test(is_expert)
def quiz_builder(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=current_lesson)
    questions = quiz.questions.all().prefetch_related('answers')
    
    return render(request, 'quizzes/quiz_builder.html', {
        'quiz': quiz,
        'questions': questions,
        'current_lesson': current_lesson,
    })


@user_passes_test(is_expert)
def update_quiz(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=current_lesson)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, _('Тест успешно изменен.'))
            return redirect('open_quiz_builder', username=request.user.username, course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/update_quiz.html', {
        'form': form,
        'quiz': quiz,
        'current_course': current_course,
        'current_lesson': current_lesson,
    })


@require_POST
@user_passes_test(is_expert)
def delete_quiz(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson=current_lesson)

    quiz.delete()
    messages.success(request, _('Тест успешно удален.'))

    return redirect('studio_lessons', username=current_course.author.username, course_id=current_course.id)


@user_passes_test(is_expert)
def add_question(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    current_quiz = get_object_or_404(Quiz, id=quiz_id, lesson=current_lesson)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = current_quiz

            formset = AnswerFormSet(request.POST, instance=question)

            if formset.is_valid():
                question.save() 
                formset.save() 
                
                messages.success(request, _('Вопрос успешно добавлен.'))
                
                if 'save_and_add_another' in request.POST:
                    return redirect('add_question', username=username, course_id=course_id, lesson_order_num=lesson_order_num, quiz_id=quiz_id)
                
                return redirect('open_quiz_builder', username=username, course_id=course_id, lesson_order_num=lesson_order_num, quiz_id=quiz_id)
        else:
            formset = AnswerFormSet(request.POST)
    else:
        form = QuestionForm()
        formset = AnswerFormSet()

    return render(request, 'quizzes/create_question.html', {
        'form': form,
        'formset': formset,
        'quiz': current_quiz,
        'current_course': current_course,
    })


@require_POST
@user_passes_test(is_expert)
def delete_question(request, username, course_id, lesson_order_num, quiz_id, question_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    current_quiz = get_object_or_404(Quiz, id=quiz_id, lesson=current_lesson)
    question = get_object_or_404(Question, id=question_id, quiz=current_quiz)

    question.delete()
    messages.success(request, _('Вопрос успешно удален.'))

    return redirect('open_quiz_builder', username=username, course_id=course_id, lesson_order_num=lesson_order_num, quiz_id=quiz_id)


@user_passes_test(is_expert)
def update_question(request, username, course_id, lesson_order_num, quiz_id, question_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    current_quiz = get_object_or_404(Quiz, id=quiz_id, lesson=current_lesson)
    question = get_object_or_404(Question, id=question_id, quiz=current_quiz)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        
        if form.is_valid():
            updated_question = form.save(commit=False)
            formset = AnswerFormSet(request.POST, instance=updated_question)

            if formset.is_valid():
                updated_question.save() 
                formset.save() 
                
                messages.success(request, _('Вопрос успешно изменен.'))
                return redirect('open_quiz_builder', username=username, course_id=course_id, 
                                lesson_order_num=lesson_order_num, quiz_id=quiz_id)
        else:
            formset = AnswerFormSet(request.POST, instance=question)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'quizzes/update_question.html', {
        'form': form,
        'formset': formset,
        'quiz': current_quiz,
        'current_course': current_course,
        'question': question,
    })


@login_required
def quiz_result(request, course_id, lesson_order_num, quiz_id, progress_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)
    current_quiz = get_object_or_404(Quiz, pk=quiz_id, lesson=current_lesson)
    progress = get_object_or_404(QuizProgress, id=progress_id, user=request.user, quiz=current_quiz)
    
    total_questions = current_quiz.questions.count()
    percent = (progress.score / total_questions * 100) if total_questions > 0 else 0
    
    return render(request, 'quizzes/quiz_result.html', {
        'progress': progress,
        'total': total_questions,
        'percent': round(percent),
        'current_course': current_course,
        'current_lesson': current_lesson
    })