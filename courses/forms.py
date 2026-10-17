from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Course, Lesson
from .widgets import TipTapWidget

User = get_user_model()


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course

        fields = ('title', 'description')

        labels = {
            'title': _('Название курса'),
            'description': _('Описание курса'),
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'placeholder': _('О чем этот курс?')}),
        }


class UpdateCourseForm(forms.ModelForm):
    class Meta:
        model = Course

        fields = ('title', 'description')

        labels = {
            'title': _('Название курса'),
            'description': _('Описание курса'),
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'placeholder': _('О чем этот курс?')}),
        }


class CreateLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'content')

        labels = {
            'title': _('Название урока'),
            'content': _('Теоретическая часть урока'),
            'order_num': _('Порядковый номер урока'),
        }

        widgets = {
            'content': TipTapWidget(),
        }


class UpdateLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'content')

        labels = {
            'title': _('Название урока'),
            'content': _('Теоретическая часть урока'),
            'order_num': _('Порядковый номер урока'),
        }

        widgets = {
            'content': TipTapWidget(),
        }