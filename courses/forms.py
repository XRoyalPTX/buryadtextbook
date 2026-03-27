from django import forms
from django.contrib.auth import get_user_model
from .models import Course

User = get_user_model()


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course

        fields = ('title', 'description')

        labels = {
            'title': 'Название курса',
            'description': 'Описание курса',
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'placeholder': 'О чем этот курс?'}),
        }


class UpdateCourseForm(forms.ModelForm):
    class Meta:
        model = Course

        fields = ('title', 'description')

        labels = {
            'title': 'Название курса',
            'description': 'Описание курса',
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'placeholder': 'О чем этот курс?'}),
        }