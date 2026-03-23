from django.test import TestCase
from .models import MyUser

# Create your tests here.


class MyUserTest(TestCase):
    def test_user_str(self):
        user = MyUser.objects.create(username="xroyalptx",first_name="Владислав",last_name="Архинчеев",email="vladik@ya.ru",password="clown")
        checkItem = str(user)
        self.assertEqual(checkItem, "Логин: xroyalptx\nРоль: Студент\nИмя: Владислав\nФамилия: Архинчеев\nЭлектронная почта: vladik@ya.ru")
        pass