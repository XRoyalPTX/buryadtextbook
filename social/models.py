from django.db import models
from users.models import MyUser
from courses.models import Lesson
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator 


class Comment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')

    text = models.TextField(
        "Комментарий",
        validators=[
            MinLengthValidator(1, message="Комментарий слишком короткий (минимум 1 символ)."),
            MaxLengthValidator(1000, message="Комментарий не может быть длиннее 1000 символов.")
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    
    is_deleted = models.BooleanField("Удален", default=False)
    deleted_at = models.DateTimeField("Время удаления", null=True, blank=True)
    deleted_by = models.ForeignKey(
        MyUser, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='deleted_comments', 
        verbose_name="Кем удален"
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def get_thread_replies(self):
        return self.replies.all().order_by('created_at')

    def __str__(self):
        return f"Комментарий от {self.user.username} к уроку {self.lesson.title}"

class Like(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"

    def __str__(self):
        return f"Лайк от {self.user.username} к уроку {self.lesson.title}"