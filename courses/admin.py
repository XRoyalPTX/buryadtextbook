from django.contrib import admin

# Register your models here.

from .models import Course, Lesson, CourseProgress, LessonProgress

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(CourseProgress)
admin.site.register(LessonProgress)