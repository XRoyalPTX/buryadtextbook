from django.shortcuts import render, redirect
from courses.models import Course, Lesson, LessonProgress
from .models import Quiz, Question, QuizProgress
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import QuizForm, QuestionForm, AnswerFormSet
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib import messages
from django.utils import timezone

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
            lesson_progress, _ = LessonProgress.objects.get_or_create(
                user=request.user, 
                lesson=current_lesson
            )
            if not lesson_progress.complete_date:
                lesson_progress.complete_date = timezone.now()
                lesson_progress.save()
        
        return redirect('quiz_result', course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=current_quiz.id, progress_id=progress.id)

    return render(request, 'quizzes/quiz.html', {
        'current_course': current_course,
        'current_lesson': current_lesson,
        'current_quiz': current_quiz,
    })

@login_required
def create_quiz(request, username, course_id, lesson_order_num):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()

    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course__id=course_id)
    
    if hasattr(current_lesson, 'quiz'):
        return redirect('update_quiz', username=request.user.username, course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=current_lesson.quiz.id) 

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = current_lesson 
            quiz.save()
            messages.success(request, 'Тест успешно создан.')
            return redirect('open_quiz_builder', username=request.user.username, course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'quizzes/create_quiz.html', {
        'form': form,
        'current_lesson': current_lesson,
    })


@login_required
def quiz_builder(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('answers')
    
    return render(request, 'quizzes/quiz_builder.html', {
        'quiz': quiz,
        'questions': questions,
        'current_lesson': current_lesson,
    })


@login_required
def update_quiz(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тест успешно изменен.')
            return redirect('open_quiz_builder', username=request.user.username, course_id=current_course.id, lesson_order_num=current_lesson.order_num, quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/update_quiz.html', {
        'form': form,
        'quiz': quiz,
        'current_course': current_course,
        'current_lesson': current_lesson,
    })


@login_required
def delete_quiz(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()
    
    current_lesson = get_object_or_404(Lesson, course=current_course, order_num=lesson_order_num)

    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Тест успешно удален.')

    return redirect('studio_lessons', username=current_course.author.username, course_id=current_course.id)


@login_required
def add_question(request, username, course_id, lesson_order_num, quiz_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()
    
    current_quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = current_quiz

            formset = AnswerFormSet(request.POST, instance=question)

            if formset.is_valid():
                question.save() 
                formset.save() 
                
                messages.success(request, 'Вопрос успешно добавлен.')
                
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


@login_required
def delete_question(request, username, course_id, lesson_order_num, quiz_id, question_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()
    
    question = get_object_or_404(Question, id=question_id, quiz__id=quiz_id)

    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Вопрос успешно удален.')

    return redirect('open_quiz_builder', username=username, course_id=course_id, lesson_order_num=lesson_order_num, quiz_id=quiz_id)


@login_required
def update_question(request, username, course_id, lesson_order_num, quiz_id, question_id):
    if request.user.username != username and not request.user.is_superuser:
        raise PermissionDenied()
    
    current_course = get_object_or_404(Course, id=course_id)
    if request.user != current_course.author:
        raise PermissionDenied()
    
    current_quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=current_quiz)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        
        if form.is_valid():
            updated_question = form.save(commit=False)
            formset = AnswerFormSet(request.POST, instance=updated_question)

            if formset.is_valid():
                updated_question.save() 
                formset.save() 
                
                messages.success(request, 'Вопрос успешно изменен.')
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
    progress = get_object_or_404(QuizProgress, id=progress_id, user=request.user)
    
    total_questions = progress.quiz.questions.count()
    percent = (progress.score / total_questions * 100) if total_questions > 0 else 0
    
    return render(request, 'quizzes/quiz_result.html', {
        'progress': progress,
        'total': total_questions,
        'percent': round(percent),
        'current_course': progress.quiz.lesson.course,
        'current_lesson': progress.quiz.lesson
    })