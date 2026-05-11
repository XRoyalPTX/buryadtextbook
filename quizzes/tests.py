from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from courses.models import Course, Lesson, LessonProgress
from .models import Quiz, Question, Answer, QuizProgress
from .forms import QuizForm, AnswerFormSet

User = get_user_model()

class QuizBaseTest(TestCase):
    def setUp(self):
        self.expert = User.objects.create_user(username='expert_user', password='123', email='expert@test.com', role='expert')
        self.student = User.objects.create_user(username='student_user', password='123', email='student@test.com', role='student')
        self.hacker = User.objects.create_user(username='hacker_user', password='123', email='hacker@test.com', role='expert')

        self.course = Course.objects.create(title="Курс", description="...", author=self.expert)
        self.lesson = Lesson.objects.create(title="Урок", content="...", course=self.course, order_num=1)
        self.quiz = Quiz.objects.create(lesson=self.lesson, title="Тест 1", description="Описание")

        self.q_single = Question.objects.create(quiz=self.quiz, text="Q1", type='single_choice')
        self.a1 = Answer.objects.create(question=self.q_single, text="Верно", is_correct=True)
        self.a2 = Answer.objects.create(question=self.q_single, text="Неверно", is_correct=False)


class QuizModelTest(QuizBaseTest):
    def test_check_answer_logic(self):
        self.assertTrue(self.q_single.check_answer([str(self.a1.id)]))
        self.assertFalse(self.q_single.check_answer([str(self.a2.id)]))
        self.assertFalse(self.q_single.check_answer([]))

    def test_calculate_result_passed(self):
        progress = QuizProgress.objects.create(user=self.student, quiz=self.quiz)
        user_answers = {str(self.q_single.id): [str(self.a1.id)]}
        
        progress.calculate_and_save_result(user_answers)
        self.assertEqual(progress.score, 1)
        self.assertTrue(progress.is_passed)

    def test_calculate_result_failed(self):
        progress = QuizProgress.objects.create(user=self.student, quiz=self.quiz)
        user_answers = {str(self.q_single.id): [str(self.a2.id)]}
        
        progress.calculate_and_save_result(user_answers)
        self.assertFalse(progress.is_passed)

    def test_calculate_result_no_questions(self):
        empty_quiz = Quiz.objects.create(lesson=Lesson.objects.create(title="L2", course=self.course), title="Empty")
        progress = QuizProgress.objects.create(user=self.student, quiz=empty_quiz)
        progress.calculate_and_save_result({})
        self.assertEqual(progress.score, 0)


class QuizFormTest(QuizBaseTest): 
    def test_answer_formset_validation(self):
        question = Question(quiz=self.quiz, text="?", type='single_choice')

        data = {
            'answers-TOTAL_FORMS': '2',
            'answers-INITIAL_FORMS': '0',
            'answers-0-text': 'A1',
            'answers-0-is_correct': 'on',
            'answers-1-text': 'A2',
            'answers-1-is_correct': 'on',
        }
        formset = AnswerFormSet(data, instance=question)
        self.assertFalse(formset.is_valid())

    def test_answer_formset_no_answers(self):
        question = Question(quiz=self.quiz, text="?", type='single_choice')
        data = {
            'answers-TOTAL_FORMS': '0',
            'answers-INITIAL_FORMS': '0',
        }
        formset = AnswerFormSet(data, instance=question)
        self.assertFalse(formset.is_valid())

    def test_multiple_choice_validation(self):
        question = Question(quiz=self.quiz, text="?", type='multiple_choice')
        data = {
            'answers-TOTAL_FORMS': '1',
            'answers-INITIAL_FORMS': '0',
            'answers-0-text': 'A1',
            'answers-0-is_correct': '', 
        }
        formset = AnswerFormSet(data, instance=question)
        self.assertFalse(formset.is_valid())


class QuizViewsTest(QuizBaseTest):
    def test_open_quiz_permissions(self):
        self.client.login(username='student_user', password='123')
        url = reverse('open_quiz', args=[self.course.id, self.lesson.order_num, self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_expert_access_studio_builder(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('open_quiz_builder', kwargs={
            'username': 'expert_user',
            'course_id': self.course.id,
            'lesson_order_num': self.lesson.order_num,
            'quiz_id': self.quiz.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_hacker_cannot_access_builder(self):
        self.client.login(username='hacker_user', password='123')
        url = reverse('open_quiz_builder', kwargs={
            'username': 'expert_user', 
            'course_id': self.course.id,
            'lesson_order_num': self.lesson.order_num,
            'quiz_id': self.quiz.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_create_quiz_view(self):
        self.client.login(username='expert_user', password='123')
        lesson_no_quiz = Lesson.objects.create(title="L2", content="...", course=self.course, order_num=2)
        url = reverse('create_quiz', kwargs={
            'username': 'expert_user',
            'course_id': self.course.id,
            'lesson_order_num': lesson_no_quiz.order_num
        })
        response = self.client.post(url, {'title': 'New Quiz', 'description': 'Desc'})
        self.assertEqual(Quiz.objects.filter(title='New Quiz').count(), 1)

    def test_submit_quiz_success(self):
        self.client.login(username='student_user', password='123')
        url = reverse('open_quiz', args=[self.course.id, self.lesson.order_num, self.quiz.id])
        
        post_data = {f'question_{self.q_single.id}': [str(self.a1.id)]}
        response = self.client.post(url, post_data)
        
        progress = QuizProgress.objects.get(user=self.student, quiz=self.quiz)
        self.assertTrue(progress.is_passed)
        
        lesson_progress = LessonProgress.objects.get(user=self.student, lesson=self.lesson)
        self.assertIsNotNone(lesson_progress.complete_date)
        
        self.assertRedirects(response, reverse('quiz_result', args=[self.course.id, self.lesson.order_num, self.quiz.id, progress.id]))

    def test_delete_quiz(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('delete_quiz', kwargs={
            'username': 'expert_user',
            'course_id': self.course.id,
            'lesson_order_num': self.lesson.order_num,
            'quiz_id': self.quiz.id
        })
        self.client.post(url)
        self.assertFalse(Quiz.objects.filter(id=self.quiz.id).exists())

    def test_update_quiz_post(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('update_quiz', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        })
        response = self.client.post(url, {'title': 'Updated Title', 'description': 'New Desc'})
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Updated Title')
        self.assertRedirects(response, reverse('open_quiz_builder', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        }))

    def test_add_question_full_post(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('add_question', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        })
        data = {
            'text': 'Новый сложный вопрос',
            'type': 'single_choice',
            'answers-TOTAL_FORMS': '2',
            'answers-INITIAL_FORMS': '0',
            'answers-0-text': 'Верный ответ',
            'answers-0-is_correct': 'on',
            'answers-1-text': 'Ложный ответ',
            'answers-1-is_correct': '',
        }
        response = self.client.post(url, data)
        self.assertEqual(Question.objects.filter(text='Новый сложный вопрос').count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_update_question_post(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('update_question', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id,
            'question_id': self.q_single.id
        })
        data = {
            'text': 'Измененный текст вопроса',
            'type': 'single_choice',
            'answers-TOTAL_FORMS': '1',
            'answers-INITIAL_FORMS': '1',
            'answers-0-id': self.a1.id,
            'answers-0-text': 'Новый текст ответа',
            'answers-0-is_correct': 'on',
        }
        self.client.post(url, data)
        self.q_single.refresh_from_db()
        self.assertEqual(self.q_single.text, 'Измененный текст вопроса')

    def test_delete_question_post(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('delete_question', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id,
            'question_id': self.q_single.id
        })
        response = self.client.post(url)
        self.assertFalse(Question.objects.filter(id=self.q_single.id).exists())
        self.assertRedirects(response, reverse('open_quiz_builder', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        }))

    def test_create_quiz_already_exists(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('create_quiz', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 'lesson_order_num': self.lesson.order_num
        })
        response = self.client.get(url)
        self.assertRedirects(response, reverse('update_quiz', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        }))

    def test_update_quiz_post(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('update_quiz', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        })
        response = self.client.post(url, {'title': 'Новое название', 'description': 'Новое описание'})
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Новое название')

    def test_add_question_and_add_another(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('add_question', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id
        })
        data = {
            'text': 'Вопрос 2',
            'type': 'single_choice',
            'answers-TOTAL_FORMS': '1',
            'answers-INITIAL_FORMS': '0',
            'answers-0-text': 'Верно',
            'answers-0-is_correct': 'on',
            'save_and_add_another': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Question.objects.filter(text='Вопрос 2').exists())

    def test_update_question_post(self):
        self.client.login(username='expert_user', password='123')
        url = reverse('update_question', kwargs={
            'username': 'expert_user', 'course_id': self.course.id, 
            'lesson_order_num': self.lesson.order_num, 'quiz_id': self.quiz.id,
            'question_id': self.q_single.id
        })
        data = {
            'text': 'Обновленный вопрос',
            'type': 'single_choice',
            'answers-TOTAL_FORMS': '1',
            'answers-INITIAL_FORMS': '1',
            'answers-0-id': self.a1.id,
            'answers-0-text': 'Обновленный ответ',
            'answers-0-is_correct': 'on',
        }
        self.client.post(url, data)
        self.q_single.refresh_from_db()
        self.assertEqual(self.q_single.text, 'Обновленный вопрос')

    def test_quiz_result_view(self):
        self.client.login(username='student_user', password='123')
        progress = QuizProgress.objects.create(user=self.student, quiz=self.quiz, score=1, is_passed=True)
        url = reverse('quiz_result', args=[self.course.id, self.lesson.order_num, self.quiz.id, progress.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['percent'], 100)