from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator 
from django.contrib.auth.validators import UnicodeUsernameValidator


# Create your models here.

class MyUser(AbstractUser):

    username = models.CharField(
        _("username"),
        max_length=20, 
        unique=True,
        help_text=_(
            "Обязательное поле. От 3 до 20 символов. Только буквы, цифры и знаки @/./+/-/_."
        ),
        validators=[
            UnicodeUsernameValidator(),
            MinLengthValidator(3, message=_("Никнейм должен содержать минимум 3 символа.")),
            MaxLengthValidator(20, message=_("Никнейм не может быть длиннее 20 символов."))
        ],
        error_messages={
            "unique": _("Пользователь с таким никнеймом уже существует."),
        },
    )

    first_name = models.CharField(
        _("first name"), 
        max_length=50, 
        blank=False,
        validators=[
            MinLengthValidator(1, message=_("Имя должно содержать минимум 1 символ.")),
            MaxLengthValidator(50, message=_("Имя не может быть длиннее 50 символов."))
        ]
    )

    last_name = models.CharField(
        _("last name"), 
        max_length=50, 
        blank=False,
        validators=[
            MinLengthValidator(1, message=_("Фамилия должна содержать минимум 1 символ.")),
            MaxLengthValidator(50, message=_("Фамилия не может быть длиннее 50 символов."))
        ]
    )

    email = models.EmailField(unique=True, verbose_name=_("Email"))

    STUDENT = "student"
    EXPERT = "expert"

    ROLE_CHOICES = [
        (STUDENT, _('Студент')),
        (EXPERT, _('Эксперт')),
    ]

    streak_count = models.PositiveIntegerField(_("Ударная серия"), default=0)
    last_activity_date = models.DateField(_("Дата последней активности"), default='1900-1-1')

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )

    def __str__(self):
        return f"Логин: {self.username}\nРоль: {self.get_role_display()}\nИмя: {self.first_name}\nФамилия: {self.last_name}\nЭлектронная почта: {self.email}"
