from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpRequest, HttpResponse, Http404
from django.utils.translation import gettext_lazy as _

from courses.models import Course, Lesson, CourseProgress
from users.models import MyUser
from .models import Comment, Like

from django.core.exceptions import PermissionDenied
from django.utils import timezone

# Create your views here.


def _check_lesson_access(user, course, lesson):
    is_owner_or_admin = (user == course.author or user.is_superuser)
    if not is_owner_or_admin:
        if not course.is_published or not lesson.is_published:
            raise Http404("Урок не найден.")
        if not CourseProgress.objects.filter(course=course, user=user).exists():
            raise PermissionDenied("Для взаимодействия с уроком необходимо начать курс.")


@require_POST
@login_required
def press_like(request, course_id, lesson_order_num):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    _check_lesson_access(request.user, current_course, current_lesson)

    current_user = request.user
    current_like = Like.objects.filter(lesson=current_lesson, user=current_user)
    if current_like.exists():
        current_like.delete()
        user_liked = False
    else:
        Like.objects.create(lesson=current_lesson, user=current_user)
        user_liked = True

    likes_cnt = Like.objects.filter(lesson=current_lesson).count()
    
    return render(request, 'social/like_button.html', {
        'user_liked': user_liked,
        'current_course': current_course,
        'current_lesson': current_lesson,
        'likes_cnt': likes_cnt,
    })


@require_POST
@login_required
def add_comment(request, course_id, lesson_order_num):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    _check_lesson_access(request.user, current_course, current_lesson)
    
    input_text = (request.POST.get('text') or '').strip()
    if not input_text or len(input_text) > 1000:
        return HttpResponse("Длина комментария должна быть от 1 до 1000 символов.", status=400)

    parent_id = request.POST.get('parent_id')
    parent_obj = None

    if parent_id:
        try:
            parent_obj = Comment.objects.filter(
                id=int(parent_id), 
                lesson=current_lesson,
                is_deleted=False
            ).first()
            if parent_obj and parent_obj.parent:
                parent_obj = parent_obj.parent
        except (ValueError, TypeError):
            parent_obj = None

    new_comment = Comment.objects.create(
        user=request.user, 
        lesson=current_lesson, 
        text=input_text,
        parent=parent_obj 
    )

    return render(request, 'social/comment_item.html', {
        'comment': new_comment,
        'current_course': current_course,
        'current_lesson': current_lesson
    })


@login_required
def get_reply_form(request, course_id, lesson_order_num, comment_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    _check_lesson_access(request.user, current_course, current_lesson)

    comment_to_reply = get_object_or_404(Comment, id=comment_id, lesson=current_lesson, is_deleted=False)
    root_comment = comment_to_reply.parent if comment_to_reply.parent else comment_to_reply
    
    return render(request, 'social/reply_form.html', {
        'parent_comment': comment_to_reply, 
        'root_comment': root_comment, 
        'course_id': course_id,
        'lesson_order_num': lesson_order_num,
    })


@require_POST
@login_required
def delete_comment(request, course_id, lesson_order_num, comment_id):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    comment = get_object_or_404(Comment, id=comment_id, lesson=current_lesson)

    if not (request.user == comment.user or request.user == current_course.author or request.user.is_superuser):
        raise PermissionDenied("У вас нет прав для удаления этого комментария.")

    if not comment.is_deleted:
        comment.is_deleted = True
        comment.deleted_at = timezone.now()
        comment.deleted_by = request.user
        comment.save()

    return render(request, 'social/comment_item.html', {
        'comment': comment,
        'current_course': current_course,
        'current_lesson': current_lesson
    })
