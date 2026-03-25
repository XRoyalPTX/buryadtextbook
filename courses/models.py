from django.db import models
from users.models import MyUser
from django.utils import timezone

# Create your models here.


class Course(models.Model):
    picture = models.ImageField(upload_to='static/courses/images/courses_imgs', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"Курс: {self.title};\nАвтор: {self.author.last_name} {self.author.first_name}"


class Lesson(models.Model):
    picture = models.ImageField(upload_to='static/courses/images/lessons_imgs', null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    order_num = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['course', 'order_num']]

    def __str__(self):
        return f"Урок №{self.order_num} из курса «{self.course.title}»"
