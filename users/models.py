from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class MyUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email")

    STUDENT = "student"
    EXPERT = "expert"

    ROLE_CHOICES = [
        (STUDENT, 'Студент'),
        (EXPERT, 'Эксперт'),
    ]

    streak_count = models.PositiveIntegerField("Ударная серия", default=0)
    last_activity_date = models.DateField("Дата последней активности", default='1900-1-1')

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )

    def __str__(self):
        return f"Логин: {self.username}\nРоль: {self.get_role_display()}\nИмя: {self.first_name}\nФамилия: {self.last_name}\nЭлектронная почта: {self.email}"
