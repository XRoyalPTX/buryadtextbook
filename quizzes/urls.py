from django.urls import path
from . import views


urlpatterns = [
    path('courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/<int:quiz_id>/', views.open_quiz, name='open_quiz'),
    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/create/', views.create_quiz, name='create_quiz'),
    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/builder/<int:quiz_id>', views.quiz_builder, name='open_quiz_builder'),
    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/builder/<int:quiz_id>/update_quiz', views.update_quiz, name='update_quiz'),
    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/builder/<int:quiz_id>/delete_quiz', views.delete_quiz, name='delete_quiz'),

    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/builder/<int:quiz_id>/add_question', views.add_question, name='add_question'),
    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/builder/<int:quiz_id>/delete_question/<int:question_id>', views.delete_question, name='delete_question'),
    path('studio/<str:username>/courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/builder/<int:quiz_id>/update_question/<int:question_id>', views.update_question, name='update_question'),

    path('courses/<int:course_id>/lesson/<int:lesson_order_num>/quiz/<int:quiz_id>/result/<int:progress_id>/', views.quiz_result, name='quiz_result')
]
