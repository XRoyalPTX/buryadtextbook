from django.db import models
from users.models import MyUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxLengthValidator, MinLengthValidator
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Course(models.Model):
    title = models.CharField(
        _("Название курса"), 
        max_length=100, 
        validators=[MaxLengthValidator(100, message=_("Название курса не может быть длиннее 100 символов."))]
    )
    description = models.TextField(
        _("Описание курса"),
        validators=[MaxLengthValidator(1500, message=_("Описание курса не может быть длиннее 1500 символов."))]
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE, 
        verbose_name=_("Автор"),
        limit_choices_to={"role": "expert"}
    )
    is_published = models.BooleanField(default=False, verbose_name=_("Опубликовано"))
    date_created = models.DateField(_("Дата создания"), auto_now_add=True)
    date_updated = models.DateField(_("Последнее изменение"), auto_now=True)


    def clean(self):
        if self.pk and self.is_published and self.lessons.filter(is_published=True).count() == 0:
            raise ValidationError(_('Нельзя опубликовать курс, у которого нет опубликованных уроков. Опубликуйте хотя бы один урок из этого курса для публикации самого курса.'))

        if not hasattr(self, 'author') or self.author is None:
            return 
        
        if self.author.role != "expert" and not self.author.is_superuser:
            raise ValidationError(_('Автором курса может быть только пользователь с ролью "Эксперт"'))


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
    title = models.CharField(
        _("Название урока"), 
        max_length=120,
        validators=[MaxLengthValidator(120, message=_("Название урока не может быть длиннее 120 символов."))]
    )
    content = models.TextField(
        _("Контент урока"),
        validators=[MaxLengthValidator(50000, message=_("Контент урока слишком огромный (максимум 50 000 символов вместе с разметкой)."))]
    )
    order_num = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name=_("Порядковый номер урока"))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name=_("Курс"))
    is_published = models.BooleanField(default=False, verbose_name=_("Опубликовано"))

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
    start_date = models.DateTimeField(_("Дата начала прохождения курса"), auto_now_add=True)
    complete_date = models.DateTimeField(_("Дата завершения курса"), null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progresses', verbose_name=_("Курс"))
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='course_progresses', verbose_name=_("Студент"))

    class Meta:
        unique_together = [['course', 'user']]

    def __str__(self):
        return f"Прохождение курса {self.course.title} пользователем {self.user.username}»"
    

class LessonProgress(models.Model):
    start_date = models.DateTimeField(_("Дата начала прохождения урока"), auto_now_add=True)
    complete_date = models.DateTimeField(_("Дата завершения урока"), null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses', verbose_name=_("Урок"))
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='lesson_progresses', verbose_name=_("Студент"))

    class Meta:
        unique_together = [['lesson', 'user']]

    def __str__(self):
        return f"Прохождение урока {self.lesson.title} пользователем {self.user.username}»"