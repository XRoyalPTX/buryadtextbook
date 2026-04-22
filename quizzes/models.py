from django.db import models
from courses.models import Lesson
from users.models import MyUser
from django.core.exceptions import ValidationError

# Create your models here.


class Quiz(models.Model):
    lesson = models.OneToOneField(
        Lesson, 
        on_delete=models.CASCADE,
        related_name='quiz',
    )
    title = models.CharField("Название теста", max_length=255)
    description = models.TextField("Описание теста")

    def __str__(self):
        return f"Тест {self.title} к уроку {self.lesson.title}"


class Question(models.Model):

    types_choices = [
        ('single_choice', 'Один правильный ответ'),
        ('multiple_choice', 'Несколько правильных ответов')
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=511)
    content = models.TextField(null=True, blank=True)
    type = models.CharField(
        max_length=40,
        choices=types_choices,
        default='unknown'
    )

    def check_answer(self, submitted_answer_ids):
        if not submitted_answer_ids:
            return False

        correct_answer_ids = self.answers.filter(
            is_correct=True
        ).values_list('id', flat=True)

        int_submitted_answer_ids = [int(item) for item in submitted_answer_ids]
        
        return set(int_submitted_answer_ids) == set(correct_answer_ids)

    def __str__(self):
        return f"Вопрос к тесту {self.quiz.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField("Текст ответа", max_length=255)
    is_correct = models.BooleanField("Правильность ответа")

    def __str__(self):
        status = 'Правильный' if self.is_correct else 'Неправильный'
        return f"{status} ответ: {self.text}. Из вопроса: {self.question.text}"
    

class QuizProgress(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='quiz_progress')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='progresses')
    pass_date = models.DateTimeField("Дата прохождения", auto_now_add=True)
    is_passed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    
    def calculate_and_save_result(self, user_answers):
        correct_count = 0
        all_questions = self.quiz.questions.all()
        total_questions = all_questions.count()

        if total_questions == 0:
            return

        for question in all_questions:
            question_answers = user_answers.get(str(question.id), [])
            if question.check_answer(question_answers):
                correct_count += 1

        score_per = (correct_count / total_questions) * 100
        
        self.score = correct_count
        self.is_passed = score_per >= 60
        self.save()

    def __str__(self):
        status = 'Успешное' if self.is_passed else 'Безуспешное'
        return f"{status} прохождение теста {self.quiz.title} пользователем {self.user.username}. Результат: {self.score}"
