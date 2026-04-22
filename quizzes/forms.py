from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название теста'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание теста'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'type', 'content']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Текст вопроса'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Дополнительный контент (при необходимости)'}),
        }


class BaseAnswerFormSet(BaseInlineFormSet):
    def clean(self):
        """Проверка количества правильных ответов перед сохранением"""
        super().clean()
        
        if any(self.errors):
            return

        correct_count = 0
        filled_forms = 0

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                filled_forms += 1
                if form.cleaned_data.get('is_correct'):
                    correct_count += 1

        if filled_forms == 0:
            raise ValidationError("Добавьте хотя бы один вариант ответа.")

        question_type = self.instance.type

        if question_type == 'single_choice' and correct_count != 1:
            raise ValidationError(
                f"Для типа 'Один ответ' должен быть выбран ровно 1 верный вариант. Cейчас выбрано: {correct_count}"
            )
        
        if question_type == 'multiple_choice' and correct_count == 0:
            raise ValidationError(
                "Для типа 'Несколько ответов' выберите хотя бы один верный вариант."
            )


AnswerFormSet = inlineformset_factory(
    Question, 
    Answer, 
    fields=['text', 'is_correct'],
    formset=BaseAnswerFormSet,
    extra=5,
    max_num=10,
    can_delete=True 
)