from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson
from .models import Comment, Like

User = get_user_model()

class SocialSystemTest(TestCase):
    def setUp(self):
        self.expert = User.objects.create_user(
            username='expert_user', email='expert@social.com', password='123', role='expert'
        )
        self.student = User.objects.create_user(
            username='student_user', email='student@social.com', password='123', role='student'
        )
        
        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание", author=self.expert
        )
        self.lesson = Lesson.objects.create(
            title="Урок 1", content="Контент", course=self.course, order_num=1
        )

    def test_comment_creation_and_str(self):
        comment = Comment.objects.create(
            user=self.student, lesson=self.lesson, text="Тестовый комментарий"
        )
        self.assertEqual(str(comment), f"Комментарий от student_user к уроку {self.lesson.title}")
        self.assertEqual(Comment.objects.count(), 1)

    def test_like_unique_constraint(self):
        Like.objects.create(user=self.student, lesson=self.lesson)
        with self.assertRaises(Exception): 
            Like.objects.create(user=self.student, lesson=self.lesson)

    def test_get_thread_replies(self):
        parent = Comment.objects.create(user=self.expert, lesson=self.lesson, text="Корень")
        reply = Comment.objects.create(user=self.student, lesson=self.lesson, text="Ответ", parent=parent)
        
        self.assertIn(reply, parent.get_thread_replies())
        self.assertEqual(parent.get_thread_replies().count(), 1)

    def test_press_like_toggle_view(self):
        self.client.login(username='student_user', password='123')
        url = reverse('press_like', args=[self.course.id, self.lesson.order_num])
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 1)
        self.assertContains(response, 'liked') 

        self.client.post(url)
        self.assertEqual(Like.objects.count(), 0)

    def test_add_comment_view(self):
        self.client.login(username='student_user', password='123')
        url = reverse('add_comment', args=[self.course.id, self.lesson.order_num])
        
        response = self.client.post(url, {'text': 'Новый коммент'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.filter(parent=None).count(), 1)
        self.assertTemplateUsed(response, 'social/comment_item.html')

    def test_add_reply_flattening_logic(self):
        self.client.login(username='student_user', password='123')
        url = reverse('add_comment', args=[self.course.id, self.lesson.order_num])
        
        root = Comment.objects.create(user=self.expert, lesson=self.lesson, text="Root")
        
        level1 = Comment.objects.create(user=self.student, lesson=self.lesson, text="L1", parent=root)
        
        self.client.post(url, {'text': 'L2 (should be flat)', 'parent_id': level1.id})
        
        l2_comment = Comment.objects.latest('id')
        self.assertEqual(l2_comment.parent, root) 
        self.assertNotEqual(l2_comment.parent, level1)

    def test_get_reply_form_view(self):
        self.client.login(username='expert_user', password='123')
        comment = Comment.objects.create(user=self.student, lesson=self.lesson, text="Text")
        
        url = reverse('get_reply_form', args=[self.course.id, self.lesson.order_num, comment.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'social/reply_form.html')
        self.assertEqual(response.context['parent_comment'], comment)