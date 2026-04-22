from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Quiz, Question, Answer

class AnswerInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        correct_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                if form.cleaned_data.get('is_correct'):
                    correct_count += 1

        question_type = self.instance.type

        if question_type == 'single_choice' and correct_count != 1:
            raise ValidationError(f"Для одного ответа должен быть ровно 1 верный. Сейчас: {correct_count}")
        
        if question_type == 'multiple_choice' and correct_count == 0:
            raise ValidationError("Должен быть хотя бы один верный ответ.")

class AnswerInline(admin.TabularInline):
    model = Answer
    formset = AnswerInlineFormSet 

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]