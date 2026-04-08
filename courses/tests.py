from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Course, Lesson
from django.core.exceptions import ValidationError
from unittest.mock import patch

User = get_user_model()

class CoursePermissionsTest(TestCase):
    
    def setUp(self):
        self.student = User.objects.create_user(
            username='student_user', 
            password='testpassword123', 
            email='student@test.com',
            role='student' 
        )
        
        self.expert_author = User.objects.create_user(
            username='author_user', 
            password='testpassword123', 
            email='author@test.com',
            role='expert'
        )
        
        self.expert_hacker = User.objects.create_user(
            username='hacker_user', 
            password='testpassword123', 
            email='hacker@test.com',
            role='expert'
        )

        self.course = Course.objects.create(
            title="Основы бурятского языка",
            description="Тестовое описание курса",
            author=self.expert_author
        )

    def test_student_cannot_access_create_course(self):
        self.client.login(username='student_user', password='testpassword123')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 302)

    def test_expert_can_access_create_course(self):
        self.client.login(username='author_user', password='testpassword123')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 200)

    def test_other_expert_cannot_delete_course(self):
        self.client.login(username='hacker_user', password='testpassword123')
        response = self.client.post(reverse('delete_course', args=[self.course.id]))
        self.assertContains(response, "У вас нет прав для удаления этого курса")
        self.assertTrue(Course.objects.filter(id=self.course.id).exists())

    def test_author_can_delete_course(self):
        self.client.login(username='author_user', password='testpassword123')
        response = self.client.post(reverse('delete_course', args=[self.course.id]))
        self.assertContains(response, "Курс успешно удален")
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())


class CourseModelTest(TestCase):
    def setUp(self):
        self.expert = User.objects.create_user(username='expert', email='e@ya.ru', password='123', role='expert')
        self.student = User.objects.create_user(username='student', email='s@ya.ru', password='123', role='student')
        
        self.course = Course.objects.create(title="Тест Курс", description="Описание", author=self.expert)

    def test_course_str_method(self):
        expected_str = f"Курс: {self.course.title};\nАвтор: {self.course.author.last_name} {self.course.author.first_name}"
        self.assertEqual(str(self.course), expected_str)

    def test_lesson_str_method(self):
        lesson = Lesson.objects.create(title="Урок 1", content="Текст", course=self.course)
        expected_str = f"Урок №{lesson.order_num} из курса «{self.course.title}»"
        self.assertEqual(str(lesson), expected_str)

    def test_course_clean_author_role(self):
        bad_course = Course(title="Плохой курс", description="...", author=self.student)
        with self.assertRaises(ValidationError):
            bad_course.clean()

    def test_course_clean_publish_without_lessons(self):
        self.course.is_published = True
        
        with self.assertRaises(ValidationError):
            self.course.clean()

    def test_get_next_lesson_number_and_lesson_save(self):
        lesson1 = Lesson.objects.create(title="Введение", content="Текст", course=self.course)
        self.assertEqual(lesson1.order_num, 1)
        
        lesson2 = Lesson.objects.create(title="Продолжение", content="Текст", course=self.course)
        self.assertEqual(lesson2.order_num, 2)
        
        self.assertEqual(self.course.get_next_lesson_number(), 3)

    def test_course_auto_unpublish(self):
        lesson = Lesson.objects.create(title="Урок", content="Текст", course=self.course, is_published=True)
        self.course.is_published = True
        self.course.save()
        
        self.assertTrue(self.course.is_published)
        
        lesson.is_published = False
        lesson.save() 
        
        self.course.refresh_from_db()
        self.assertFalse(self.course.is_published)

    def test_course_clean_without_author(self):
        course_no_author = Course(title="Без автора", description="...")
        course_no_author.clean()
        self.assertTrue(True) 

    def test_course_save_unpublish_without_published_lessons(self):
        self.course.is_published = True
        self.course.save()
        
        self.assertFalse(self.course.is_published)


class CourseViewsTest(TestCase):
    def setUp(self):
        self.expert = User.objects.create_user(username='expert', email='e@test.ru', password='123', role='expert')
        self.student = User.objects.create_user(username='student', email='s@test.ru', password='123', role='student')
        
        self.course = Course.objects.create(title="Тестовый курс", description="Описание", author=self.expert)
        self.lesson = Lesson.objects.create(title="Тестовый урок", content="Контент", course=self.course)

    def test_courses_list_view(self):
        self.client.login(username='student', password='123')
        response = self.client.get(reverse('courses'))
        self.assertEqual(response.status_code, 200)

    def test_open_course_view(self):
        self.client.login(username='student', password='123')
        response = self.client.get(reverse('open_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_open_lesson_view(self):
        self.client.login(username='student', password='123')
        response = self.client.get(reverse('open_lesson', args=[self.course.id, self.lesson.order_num]))
        self.assertEqual(response.status_code, 200)

    def test_create_course_success(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('create_course'), {
            'title': 'Новый курс',
            'description': 'Описание нового курса'
        })
        self.assertRedirects(response, reverse('studio_courses', args=[self.expert.username]))
        self.assertTrue(Course.objects.filter(title='Новый курс').exists())

    def test_update_course_success(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('update_course', args=[self.course.id]), {
            'title': 'Обновленный курс',
            'description': 'Обновленное описание'
        })
        self.assertRedirects(response, reverse('studio_courses', args=[self.expert.username]))
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Обновленный курс')

    def test_create_lesson_success(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('create_lesson', args=[self.course.id]), {
            'title': 'Новый урок',
            'content': 'Текст нового урока'
        })
        self.assertRedirects(response, reverse('studio_lessons', args=[self.expert.username, self.course.id]))
        self.assertTrue(Lesson.objects.filter(title='Новый урок').exists())

    def test_update_lesson_success(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('update_lesson', args=[self.course.id, self.lesson.id]), {
            'title': 'Обновленный урок',
            'content': 'Новый текст'
        })
        self.assertRedirects(response, reverse('studio_lessons', args=[self.expert.username, self.course.id]))
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновленный урок')

    def test_studio_views(self):
        self.client.login(username='expert', password='123')
        
        response_courses = self.client.get(reverse('studio_courses', args=[self.expert.username]))
        self.assertEqual(response_courses.status_code, 200)
        
        response_lessons = self.client.get(reverse('studio_lessons', args=[self.expert.username, self.course.id]))
        self.assertEqual(response_lessons.status_code, 200)

    def test_change_order_number(self):
        self.client.login(username='expert', password='123')
        lesson2 = Lesson.objects.create(title="Урок 2", content="Текст", course=self.course)
        
        response = self.client.post(
            reverse('change_order_number', args=[self.expert.username, self.course.id]),
            {'order[]': [lesson2.id, self.lesson.id]}
        )
        self.assertEqual(response.status_code, 204) # Ожидаем успешный пустой ответ HTMX
        
        self.lesson.refresh_from_db()
        lesson2.refresh_from_db()
        self.assertEqual(lesson2.order_num, 1)
        self.assertEqual(self.lesson.order_num, 2)

    def test_htmx_publish_flow(self):
        self.client.login(username='expert', password='123')
        
        response = self.client.post(reverse('publish_lesson', args=[self.expert.username, self.course.id, self.lesson.id]))
        self.assertEqual(response.status_code, 200)
        self.lesson.refresh_from_db()
        self.assertTrue(self.lesson.is_published)

        response = self.client.post(reverse('publish_course', args=[self.expert.username, self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.course.refresh_from_db()
        self.assertTrue(self.course.is_published)

        self.client.post(reverse('unpublish_course', args=[self.expert.username, self.course.id]))
        self.course.refresh_from_db()
        self.assertFalse(self.course.is_published)

        self.client.post(reverse('unpublish_lesson', args=[self.expert.username, self.course.id, self.lesson.id]))
        self.lesson.refresh_from_db()
        self.assertFalse(self.lesson.is_published)

    def test_delete_lesson_success(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('delete_lesson', args=[self.course.id, self.lesson.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_update_course_no_changes(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('update_course', args=[self.course.id]), {
            'title': self.course.title,
            'description': self.course.description
        })
        self.assertContains(response, 'Вы не ввели никаких изменений')

    def test_update_lesson_no_changes(self):
        self.client.login(username='expert', password='123')
        response = self.client.post(reverse('update_lesson', args=[self.course.id, self.lesson.id]), {
            'title': self.lesson.title,
            'content': self.lesson.content
        })
        self.assertContains(response, 'Вы не ввели никаких изменений')

    def test_create_course_validation_error(self):
        
        with patch.object(Course, 'full_clean') as mock_clean:
            mock_clean.side_effect = ValidationError('Тестовая ошибка валидации')
            self.client.login(username='expert', password='123')
            
            response = self.client.post(reverse('create_course'), {
                'title': 'Новый курс',
                'description': 'Описание'
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Тестовая ошибка валидации')

    def test_get_forms_and_actions(self):
        self.client.login(username='expert', password='123')
        
        self.assertEqual(self.client.get(reverse('create_course')).status_code, 200)
        self.assertEqual(self.client.get(reverse('update_course', args=[self.course.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('create_lesson', args=[self.course.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('update_lesson', args=[self.course.id, self.lesson.id])).status_code, 200)
        
        self.assertEqual(self.client.get(reverse('delete_course', args=[self.course.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('delete_lesson', args=[self.course.id, self.lesson.id])).status_code, 204)

        with self.assertRaises(ValueError):
            self.client.get(reverse('publish_course', args=[self.expert.username, self.course.id]))
        with self.assertRaises(ValueError):
            self.client.get(reverse('unpublish_course', args=[self.expert.username, self.course.id]))
        with self.assertRaises(ValueError):
            self.client.get(reverse('publish_lesson', args=[self.expert.username, self.course.id, self.lesson.id]))
        with self.assertRaises(ValueError):
            self.client.get(reverse('unpublish_lesson', args=[self.expert.username, self.course.id, self.lesson.id]))

    def test_foreign_expert_permissions(self):
        User = get_user_model()
        foreign_expert = User.objects.create_user(username='hacker', email='h@ya.ru', password='123', role='expert')
        self.client.login(username='hacker', password='123')

        self.assertEqual(self.client.get(reverse('update_course', args=[self.course.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('create_lesson', args=[self.course.id])).status_code, 403)
        self.assertEqual(self.client.get(reverse('update_lesson', args=[self.course.id, self.lesson.id])).status_code, 403)
        
        self.assertEqual(self.client.post(reverse('change_order_number', args=[self.expert.username, self.course.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('publish_course', args=[self.expert.username, self.course.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('unpublish_course', args=[self.expert.username, self.course.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('publish_lesson', args=[self.expert.username, self.course.id, self.lesson.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('unpublish_lesson', args=[self.expert.username, self.course.id, self.lesson.id])).status_code, 403)

        response_delete_lesson = self.client.post(reverse('delete_lesson', args=[self.course.id, self.lesson.id]))
        self.assertContains(response_delete_lesson, "У вас нет прав для удаления этого урока")

    def test_publish_course_without_published_lessons_htmx(self):
        self.client.login(username='expert', password='123')
        self.lesson.is_published = False
        self.lesson.save()

        response = self.client.post(reverse('publish_course', args=[self.expert.username, self.course.id]))
        self.assertContains(response, "Курс не может быть опубликован")