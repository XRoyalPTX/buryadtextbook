from django.db import models
from users.models import MyUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField
from django.db.models import Max

# Create your models here.


class Course(models.Model):
    title = models.CharField("Название курса", max_length=255)
    description = models.TextField("Описание курса")
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE, 
        verbose_name="Автор",
        limit_choices_to={"role": "expert"}
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    date_created = models.DateField("Дата создания", auto_now_add=True)
    date_updated = models.DateField("Последнее изменение",auto_now=True)


    def clean(self):
        if self.pk and self.is_published and self.lessons.filter(is_published=True).count() == 0:
            raise ValidationError('Нельзя опубликовать курс, у которого нет опубликованных уроков. Опубликуйте хотя бы один урок из этого курса для публикации самого курса.')


        if not hasattr(self, 'author') or self.author is None:
            return 
        
        if self.author.role != "expert" and not self.author.is_superuser:
            raise ValidationError('Автором курса может быть только пользователь с ролью "Эксперт"')


    def __str__(self):
        return f"Курс: {self.title};\nАвтор: {self.author.last_name} {self.author.first_name}"
    

    def get_next_lesson_number(self):
        stats = self.lessons.aggregate(
            maximum=Max('order_num', default=0)
        )
        return stats['maximum'] + 1
    
    def save(self, *args, **kwargs):
        if self.is_published and self.pk and self.lessons.filter(is_published=True).count() == 0:
            self.is_published = False
        
        super().save(*args, **kwargs)


class Lesson(models.Model):
    title = models.CharField("Название урока", max_length=255)
    content = RichTextField("Контент урока")
    order_num = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name="Порядковый номер урока")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")

    class Meta:
        unique_together = [['course', 'order_num']]

    def __str__(self):
        return f"Урок №{self.order_num} из курса «{self.course.title}»"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.order_num = self.course.get_next_lesson_number()

        super().save(*args, **kwargs)

        if self.course.lessons.filter(is_published=True).count() == 0:
            self.course.is_published = False
            self.course.save()

class CourseProgress(models.Model):
    start_date = models.DateTimeField("Дата начала прохождения курса", auto_now_add=True)
    complete_date = models.DateTimeField("Дата завершения курса", null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progresses', verbose_name="Курс")
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='course_progresses', verbose_name="Студент")

    class Meta:
        unique_together = [['course', 'user']]

    def __str__(self):
        return f"Прохождение курса {self.course.title} пользователем {self.user.username}»"
    

class LessonProgress(models.Model):
    start_date = models.DateTimeField("Дата начала прохождения урока", auto_now_add=True)
    complete_date = models.DateTimeField("Дата завершения урока", null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses', verbose_name="Урок")
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='lesson_progresses', verbose_name="Студент")

    class Meta:
        unique_together = [['lesson', 'user']]

    def __str__(self):
        return f"Прохождение урока {self.lesson.title} пользователем {self.user.username}»"