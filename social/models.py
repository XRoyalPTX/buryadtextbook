from django.db import models
from users.models import MyUser
from courses.models import Lesson

# Create your models here.


class Comment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
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