from django.urls import path

from . import views


urlpatterns = [
    path('', views.courses, name='courses'),

    path('create_course/', views.create_course, name='create_course'),
    path('<int:course_id>/', views.open_course, name='open_course'),
    path('update_course/<int:course_id>/', views.update_course, name='update_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),

    path('<int:course_id>/create_lesson', views.create_lesson, name='create_lesson'),
    path('<int:course_id>/lesson/<int:lesson_order_num>', views.open_lesson, name='open_lesson'),
    path('<int:course_id>/update_lesson/<int:lesson_id>', views.update_lesson, name='update_lesson'),
    path('<int:course_id>/delete_lesson/<int:lesson_id>', views.delete_lesson, name='delete_lesson'),

    path('studio/<str:username>', views.studio_courses, name='studio_courses'),
    path('studio/<str:username>/course/<int:course_id>', views.studio_lessons, name='studio_lessons'),
    path('studio/<str:username>/course/<int:course_id>/change_order_number', views.change_order_number, name='change_order_number'),
    path('studio/<str:username>/course/<int:course_id>/publish', views.publish_course, name='publish_course'),
    path('studio/<str:username>/course/<int:course_id>/unpublish', views.unpublish_course, name='unpublish_course'),
    path('studio/<str:username>/course/<int:course_id>/lesson/<int:lesson_id>/publish', views.publish_lesson, name='publish_lesson'),
    path('studio/<str:username>/course/<int:course_id>/lesson/<int:lesson_id>/unpublish', views.unpublish_lesson, name='unpublish_lesson'),

    path('<int:course_id>/start', views.create_course_progress, name='create_course_progress'),
    path('<int:course_id>/lesson/<int:lesson_order_num>/complete', views.complete_lesson, name='complete_lesson'),
]
