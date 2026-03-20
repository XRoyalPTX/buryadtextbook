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

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
