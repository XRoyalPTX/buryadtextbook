from django.urls import path

from . import views


urlpatterns = [
    path('', views.courses, name='courses'),
    path('<int:course_id>/', views.open_course, name='course'),
]
