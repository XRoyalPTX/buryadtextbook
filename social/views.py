from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from courses.models import Course, Lesson
from users.models import MyUser
from .models import Comment, Like

# Create your views here.


@login_required
def press_like(request, course_id, lesson_order_num):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    current_user = request.user
    user_liked = False

    if request.method == 'POST':
        current_like = Like.objects.filter(lesson=current_lesson, user=current_user)
        if current_like.exists():
            current_like.delete()
            user_liked = False
        else:
            new_like = Like.objects.create(lesson=current_lesson, user=current_user)
            new_like.save()
            user_liked = True

    likes_cnt = Like.objects.filter(lesson=current_lesson).count()
    
    return render(request, 'social/like_button.html', {
        'user_liked': user_liked,
        'current_course': current_course,
        'current_lesson': current_lesson,
        'likes_cnt': likes_cnt,
    })


@login_required
def add_comment(request, course_id, lesson_order_num):
    current_course = get_object_or_404(Course, pk=course_id)
    current_lesson = get_object_or_404(Lesson, order_num=lesson_order_num, course=current_course)
    
    if request.method == 'POST':
        input_text = request.POST.get('text')
        parent_id = request.POST.get('parent_id')
        parent_obj = None

        if parent_id:
            parent_obj = Comment.objects.filter(id=parent_id).first()
            if parent_obj and parent_obj.parent:
                parent_obj = parent_obj.parent

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
    
    return redirect('open_lesson', course_id=course_id, lesson_order_num=lesson_order_num)


@login_required
def get_reply_form(request, course_id, lesson_order_num, comment_id):
    comment_to_reply = get_object_or_404(Comment, id=comment_id)
    
    root_comment = comment_to_reply.parent if comment_to_reply.parent else comment_to_reply
    
    return render(request, 'social/reply_form.html', {
        'parent_comment': comment_to_reply, 
        'root_comment': root_comment, 
        'course_id': course_id,
        'lesson_order_num': lesson_order_num,
    })