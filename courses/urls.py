from django.urls import path

from . import views


urlpatterns = [
    path('', views.courses, name='courses'),
    path('create_course/', views.create_course, name='create_course'),
    path('<int:course_id>/', views.open_course, name='open_course'),
    path('update_course/<int:course_id>/', views.update_course, name='update_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('<int:course_id>/lesson/<int:lesson_order_num>', views.open_lesson, name='open_lesson'),
    path('<int:course_id>/create_lesson', views.create_lesson, name='create_lesson'),
]
